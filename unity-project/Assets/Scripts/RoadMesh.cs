﻿using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEditor;

public class RoadMesh : MonoBehaviour
{
    private class RoadEndPoint
    {
        public Vector3 leftPoint;
        public Vector3 rightPoint;
        public int leftIndex;
        public int rightIndex;
        public Vector3 tangent;
        public RoadNode.HighwayType hwyType;
        public Mesh associatedMesh;
        public Vector3 associatedIntersection;

        public RoadEndPoint(Vector3 leftPoint, Vector3 rightPoint, int leftIndex, int rightIndex, Vector3 tangent, RoadNode.HighwayType hwyType, Mesh associatedMesh)
        {
            this.leftPoint = leftPoint;
            this.rightPoint = rightPoint;
            this.leftIndex = leftIndex;
            this.rightIndex = rightIndex;
            this.tangent = tangent;
            this.hwyType = hwyType;
            this.associatedMesh = associatedMesh;
            this.associatedIntersection = Vector3.zero;
        }
    }

    private List<GameObject> _rendererGOs = new List<GameObject>();
    private float _roadWidth = 11f;
    private static float _scale = 500f;
    private static Vector2 _offset = new Vector2(-18.05f, -59.34f);

    private Dictionary<RoadNode.HighwayType, float> _uvXOffsetByHwyType = new Dictionary<RoadNode.HighwayType, float>()
    {
        {RoadNode.HighwayType.FOOTPATH, 0.75f},
        {RoadNode.HighwayType.RESIDENTIAL, 0.5f},
        {RoadNode.HighwayType.SECONDARY, 0.25f},
        {RoadNode.HighwayType.PRIMARY, 0f}
    };

    private void OnDestroy()
    {
        foreach(GameObject go in _rendererGOs)
        {
            DestroyImmediate(go);
        }
    }

    public void GenerateMeshFromPaths(List<RoadPath> paths, Dictionary<string, float> pathWidths)
    {
        // Start building path mesh
        List<Vector3> vertices = new List<Vector3>();
        List<Vector2> uvs = new List<Vector2>();
        List<int> triangles = new List<int>();
        List<Mesh> storedPathMeshes = new List<Mesh>();
        int currentMeshCounter = 0;
        int countedVertices = 0;

        Dictionary<RoadNode, List<RoadEndPoint>> intersectionNodes = new Dictionary<RoadNode, List<RoadEndPoint>>();
        foreach(RoadPath path in paths)
        {
            // First create the mesh we'll be working with
            if(storedPathMeshes.Count <= currentMeshCounter) 
            {
                storedPathMeshes.Add(new Mesh());
            }

            RoadEndPoint previousRoadEndPoint = new RoadEndPoint(Vector3.zero, Vector3.zero, -1, -1, Vector3.zero, RoadNode.HighwayType.NONE, null);
            float width = -10000f;

            RoadNode.HighwayType hwyType = RoadNode.HighwayType.NONE;

            for(int i=0; i<path.Count()-1; i++)
            {
                RoadNode a = path.Get(i);
                RoadNode b = path.Get(i+1);

                if(hwyType == RoadNode.HighwayType.NONE) hwyType = path.GetHighwayType();
                if(width == -10000f) width = pathWidths[path.GetId()];

                Vector3 posA = new Vector3(a.GetX(), 0f, a.GetY());
                Vector3 posB = new Vector3(b.GetX(), 0f, b.GetY());
                Vector3 tangent = (posB - posA).normalized;
                if(tangent == Vector3.zero)
                {
                    // TODO: Tangets should not be zero, examine why this happens earlier in the pipeline
                    Debug.LogError("Tangent is zero!");
                }
                Vector3 normal = new Vector3(tangent.z, 0f, -tangent.x)*0.001f;

                Vector3 leftStartPoint = posA + normal*_roadWidth*width;
                Vector3 rightStartPoint = posA - normal*_roadWidth*width;
                Vector3 leftEndPoint = posB + normal*_roadWidth*width;
                Vector3 rightEndPoint = posB - normal*_roadWidth*width;

                // If this is not the first path segment, merge it with the previous one
                if(previousRoadEndPoint.tangent != Vector3.zero)
                {
                    // Update start points of this segment and end points of the last segment
                    // TODO: Right now there are duplicate vertices. Find a way to count vertices so that they merge instead
                    Vector3 intersectionLeft;
                    Vector3 intersectionRight;
                    if(MathUtils.LineLineIntersection(out intersectionLeft, leftStartPoint, tangent,
                        previousRoadEndPoint.leftPoint, previousRoadEndPoint.tangent))
                    {
                        leftStartPoint = intersectionLeft;
                        // TODO: List access here may be slow, find a faster way of updating
                        vertices[vertices.Count-2] = intersectionLeft;
                    }
                    if(MathUtils.LineLineIntersection(out intersectionRight, rightStartPoint, tangent,
                        previousRoadEndPoint.rightPoint, previousRoadEndPoint.tangent))
                    {
                        rightStartPoint = intersectionRight;
                        vertices[vertices.Count-1] = intersectionRight;
                    }
                }

                vertices.Add(leftStartPoint);
                vertices.Add(rightStartPoint);
                vertices.Add(leftEndPoint);
                vertices.Add(rightEndPoint);

                triangles.Add(countedVertices);
                triangles.Add(countedVertices+1);
                triangles.Add(countedVertices+2);
                triangles.Add(countedVertices+3);
                triangles.Add(countedVertices+2);
                triangles.Add(countedVertices+1);
                countedVertices += 4;

                float roadLength = (posA - posB).magnitude;
                Vector2 uvScale = new Vector2(1f, 600*roadLength/_roadWidth);

                // Set UV x offset depending on which highway type this path is
                float uvXOffset = _uvXOffsetByHwyType[hwyType];

                uvs.Add(new Vector2(uvXOffset+0.25f, 0f) * uvScale);
                uvs.Add(new Vector2(uvXOffset, 0f) * uvScale);
                uvs.Add(new Vector2(uvXOffset+0.25f, 1f) * uvScale);
                uvs.Add(new Vector2(uvXOffset, 1f) * uvScale);

                // Set the last end point for the next path segment
                previousRoadEndPoint = new RoadEndPoint(leftEndPoint, rightEndPoint, vertices.Count-2, vertices.Count-1, tangent, hwyType, storedPathMeshes[currentMeshCounter]);
                

                if(b.IsIntersection())
                {
                    if(!intersectionNodes.ContainsKey(b))
                    {
                        intersectionNodes[b] = new List<RoadEndPoint>();
                    }
                    // Have to swap places of the right/left vertices here, at the end of the path, so that the intersection checker
                    // really looks at the left end point of a and right end point of b
                    intersectionNodes[b].Add(new RoadEndPoint(rightEndPoint, leftEndPoint, vertices.Count-1, vertices.Count-2, tangent, hwyType, storedPathMeshes[currentMeshCounter]));
                }
                // If this is the beginning or end node of the path, store it as an intersection candidate
                if(a.IsIntersection())
                {
                    if(!intersectionNodes.ContainsKey(a))
                    {
                        intersectionNodes[a] = new List<RoadEndPoint>();
                    }
                    // Negative tangent so that the tangent always points inwards to the intersection, both for a- and b-intersections
                    intersectionNodes[a].Add(new RoadEndPoint(leftStartPoint, rightStartPoint, vertices.Count-4, vertices.Count-3, -tangent, hwyType, storedPathMeshes[currentMeshCounter]));
                }
            }
            if(vertices.Count > 20000)
            {
                CreateNewMeshFilterWithMesh(vertices, triangles, uvs, storedPathMeshes[currentMeshCounter]);
                vertices.Clear();
                triangles.Clear();
                uvs.Clear();
                countedVertices = 0;
                currentMeshCounter++;
            }
        }

        // Create a last mesh to flush out any remaining vertices
        CreateNewMeshFilterWithMesh(vertices, triangles, uvs, storedPathMeshes[currentMeshCounter]);
        vertices.Clear();
        triangles.Clear();
        uvs.Clear();

        // Intersections
        foreach(RoadNode node in intersectionNodes.Keys)
        {
            // Start building path mesh
            vertices = new List<Vector3>();
            uvs = new List<Vector2>();
            triangles = new List<int>();
            Mesh intersectionMesh = new Mesh();

            List<RoadEndPoint> endPoints = intersectionNodes[node];
            //TODO: Should work for intersections with 2 nodes as well
            if(endPoints.Count <= 1)
            {
                // Skip the node if it has less than two end points. Then it is not an intersection
                continue;
            }

            // Order the end points by angle
            RoadEndPoint[] endPointsSorted = endPoints.OrderBy(v => Vector2.SignedAngle(new Vector2(v.tangent.x, v.tangent.z), Vector2.right)).ToArray();

            // Midpoint of the intersection
            Vector3 midPoint = Vector3.zero;

            // Now the end points are sorted, get them one by one
            for(int i=0; i<endPointsSorted.Length; i++)
            {
                RoadEndPoint a = endPointsSorted[i];
                RoadEndPoint b = endPointsSorted[(i+1)%endPointsSorted.Length];

                midPoint += (a.leftPoint + b.rightPoint)/2;

                string msg = "Endpoint collision check: (a.leftPoint = "
                            + a.leftPoint.x + ", " + a.leftPoint.z + "), (b.rightPoint = "
                            + b.rightPoint.x + ", " + b.rightPoint.z + "), (a.tangent = "
                            + a.tangent.x + ", " + a.tangent.z + "), b.tangent = "
                            + b.tangent.x + ", " + b.tangent.z + ")";
                
                // Get the intersection point
                // Get the right pos from end point 1 and left pos from end point 2
                Vector3 intersection = Vector3.zero;
                bool intersectionWasSet = false;
                if(MathUtils.LineLineIntersection(out intersection, a.leftPoint, a.tangent,
                    b.rightPoint, b.tangent))
                {
                    intersectionWasSet = true;
                }
                else if((a.tangent + b.tangent).magnitude < 0.01f)
                {
                    // tangents are opposite, pick the middle point
                    intersection = (a.leftPoint + b.rightPoint)/2;
                    intersectionWasSet = true;
                }
                else if((a.tangent - b.tangent).magnitude < 0.01f)
                {
                    // tangents are the same. This happens due to dirty data, but pick the middle point for now
                    intersection = (a.leftPoint + b.rightPoint)/2;
                    intersectionWasSet = true;
                }

                if(intersectionWasSet)
                {
                    // Get the vertex indices of the end points and move them to the new intersection points

                    // Since the vertices array of the mesh has read-only access, we have to copy the whole array and change the one vertex
                    Vector3[] verticesA = a.associatedMesh.vertices;
                    verticesA[a.leftIndex] = intersection;
                    a.associatedMesh.vertices = verticesA;
                    
                    Vector3[] verticesB = b.associatedMesh.vertices;
                    verticesB[b.rightIndex] = intersection;
                    b.associatedMesh.vertices = verticesB;

                    // Store the intersection on b so that the correct intersections are referenced when placing the vertices
                    b.associatedIntersection = intersection;
                    continue;
                }
                else
                {
                    Debug.LogError("Found an intersection with two incoming paths that have the same tangents! " + a.tangent + ", " + b.tangent + ". a.left = " + a.leftPoint + ", b.right = " + b.rightPoint);
                }
            }

            if(endPoints.Count > 2)
            {
                // Divide the midpoint to obtain the average
                midPoint /= endPointsSorted.Length;

                // Create intersection geometry
                for(int i=0; i< endPointsSorted.Length; i++)
                {
                    // Add the midpoint of the intersection as the next vertex
                    // Set UV x offset depending on which highway type this path is
                    RoadNode.HighwayType hwyType = endPointsSorted[i].hwyType;
                    float uvXOffset = _uvXOffsetByHwyType[hwyType];
                    uvs.Add(new Vector2(uvXOffset+0.125f, 0.5f));
                    vertices.Add(midPoint); // Add the midpoint as a new vertex for every triangle, so each triangle gets unique UV coordinates

                    Vector3 endVertex1 = endPointsSorted[i].associatedIntersection;
                    Vector3 endVertex2 = endPointsSorted[(i+1)%endPointsSorted.Length].associatedIntersection;

                    // Save the vertex to this mesh
                    vertices.Add(endVertex1);
                    vertices.Add(endVertex2);

                    // Set UV x offset depending on which highway type this path is
                    uvs.Add(new Vector2(uvXOffset, 0f)); // Every other corner get uv.x = 1 or 0
                    uvs.Add(new Vector2(uvXOffset+0.25f, 0f)); // Every other corner get uv.x = 1 or 0

                    // Create new triangles, stitch all the vertices together
                    triangles.Add(vertices.Count-3); // Mid point
                    triangles.Add(vertices.Count-2);
                    triangles.Add(vertices.Count-1);
                }

                CreateNewMeshFilterWithMesh(vertices, triangles, uvs, intersectionMesh);
            }
        }
    }

    private void CreateNewMeshFilterWithMesh(List<Vector3> vertices, List<int> triangles, List<Vector2> uvs, Mesh mesh)
    {
        GameObject go = new GameObject();
        go.transform.parent = transform;

        MeshRenderer meshRenderer = go.AddComponent(typeof(MeshRenderer)) as MeshRenderer;
        Material material = new Material(Shader.Find("Standard"));
        material.mainTexture = Resources.Load("Textures/Road") as Texture;
        meshRenderer.sharedMaterial = material;
        MeshFilter meshFilter = go.AddComponent(typeof(MeshFilter)) as MeshFilter;

        mesh.vertices = vertices.ToArray();
        mesh.triangles = triangles.ToArray();
        mesh.uv = uvs.ToArray();

        // Build normals
        Vector3[] normals = new Vector3[vertices.Count];
        for(int i=0; i<vertices.Count; i++)
        {
            normals[i] = Vector3.up;
        }
        mesh.normals = normals;

        meshFilter.mesh = mesh;

        // Store the new GameObject for later deletion
        _rendererGOs.Add(go);
    }

    public static Vector3 TransformPointToMeshSpace(Vector2 input)
    {
        return new Vector3((input.x+_offset.x)*0.5f, 0f, (input.y+_offset.y))*_scale;
    }
}
