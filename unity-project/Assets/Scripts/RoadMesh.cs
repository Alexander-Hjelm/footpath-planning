﻿using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class RoadMesh : MonoBehaviour
{
    private struct RoadEndPoint
    {
        public Vector3 leftPoint;
        public Vector3 rightPoint;
        public int leftIndex;
        public int rightIndex;
        public Vector3 tangent;

        public RoadEndPoint(Vector3 leftPoint, Vector3 rightPoint, int leftIndex, int rightIndex, Vector3 tangent)
        {
            this.leftPoint = leftPoint;
            this.rightPoint = rightPoint;
            this.leftIndex = leftIndex;
            this.rightIndex = rightIndex;
            this.tangent = tangent;
        }
    }

    private MeshFilter _meshFilter;
    private float _scale = 50f;
    private Vector2 _offset = new Vector2(-18.05f, -59.34f);

    public void Awake()
    {
        MeshRenderer meshRenderer = gameObject.AddComponent(typeof(MeshRenderer)) as MeshRenderer;
        meshRenderer.sharedMaterial = new Material(Shader.Find("Standard"));
        _meshFilter = gameObject.AddComponent(typeof(MeshFilter)) as MeshFilter;

    }

    public void GenerateMeshFromPaths(List<List<RoadNode>> paths)
    {
        Mesh mesh = new Mesh();
        float roadWidth = 1f;

        List<Vector3> vertices = new List<Vector3>();
        List<int> triangles = new List<int>();
        int countedVertices = 0;
        Dictionary<RoadNode, Queue<RoadEndPoint>> intersectionNodes = new Dictionary<RoadNode, Queue<RoadEndPoint>>();
        foreach(List<RoadNode> path in paths)
        {
            RoadEndPoint previousRoadEndPoint = new RoadEndPoint(Vector3.zero, Vector3.zero, -1, -1, Vector3.zero);

            for(int i=0; i<path.Count-1; i++)
            {
                RoadNode a = path[i];
                RoadNode b = path[i+1];
                Vector3 posA = TransformPointToMeshSpace(a.GetPosAsVector2());
                Vector3 posB = TransformPointToMeshSpace(b.GetPosAsVector2());
                Vector3 tangent = (posB - posA).normalized;
                Vector3 normal = new Vector3(tangent.z, 0f, -tangent.x)*0.001f;

                Vector3 leftStartPoint = posA + normal*roadWidth;
                Vector3 rightStartPoint = posA - normal*roadWidth;
                Vector3 leftEndPoint = posB + normal*roadWidth;
                Vector3 rightEndPoint = posB - normal*roadWidth;

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

                // Set the last end point for the next path segment
                previousRoadEndPoint = new RoadEndPoint(leftEndPoint, rightEndPoint, vertices.Count-2, vertices.Count-1, tangent);

                // If this is the beginning or end nod of the path, store it as an intersection candidate
                if(i==0)
                {
                    if(!intersectionNodes.ContainsKey(a))
                    {
                        intersectionNodes[a] = new Queue<RoadEndPoint>();
                    }
                    intersectionNodes[a].Enqueue(new RoadEndPoint(leftStartPoint, rightStartPoint, vertices.Count-4, vertices.Count-3, tangent));
                }
                if(i==path.Count-2)
                {
                    if(!intersectionNodes.ContainsKey(b))
                    {
                        intersectionNodes[b] = new Queue<RoadEndPoint>();
                    }
                    intersectionNodes[b].Enqueue(new RoadEndPoint(leftEndPoint, rightEndPoint, vertices.Count-2, vertices.Count-1, tangent));
                }
            }
        }

        // Intersections
        foreach(RoadNode node in intersectionNodes.Keys)
        {
            Queue<RoadEndPoint> endPoints = intersectionNodes[node];
            if(endPoints.Count < 2)
            {
                // Skip the node if it has less than two end points. Then it is not an intersection
                continue;
            }

            // TODO: Here: order the end points by angle
            List<RoadEndPoint> endPointsSorted = new List<RoadEndPoint>();
            while(endPoints.Count > 0)
            {
                RoadEndPoint endPoint = endPoints.Dequeue();
                endPointsSorted.Add(endPoint);
            }

            // Now the end points are sorted, get them one by one
            for(int i=0; i<endPointsSorted.Count; i++)
            {
                RoadEndPoint a = endPointsSorted[i];
                RoadEndPoint b = endPointsSorted[i+1];
                
                // Get the intersection point
                // Get the right pos from end point 1 and left pos from end point 2
                Vector3 intersection;
                if(MathUtils.LineLineIntersection(out intersection, a.rightPoint, a.tangent,
                    b.leftPoint, b.tangent))
                {
                    // Get the vertex indices of the end points and move them to the new intersection points
                    vertices[a.rightIndex] = intersection;
                    vertices[b.leftIndex] = intersection;
                    
                    // Add the intersection point as the next vertex
                    vertices.Add(intersection);

                    // Create new triangles, stitch all the vertices together
                    if(i<endPointsSorted.Count-2)
                    {
                        triangles.Add(triangles.Count-1);
                        triangles.Add(triangles.Count);
                        triangles.Add(triangles.Count+1);
                    }
                    continue;
                }
                
                Debug.LogError("Found an intersection with two incoming paths that have the same tangents!");

            }
        }

        mesh.vertices = vertices.ToArray();
        mesh.triangles = triangles.ToArray();

        // Build normals
        Vector3[] normals = new Vector3[vertices.Count];
        for(int i=0; i<vertices.Count; i++)
        {
            normals[i] = Vector3.up;
        }
        mesh.normals = normals;

        //Debug.Log(mesh.triangles.Count());
        //mesh.uv = newUV;
        
        _meshFilter.mesh = mesh;
    }

    private Vector3 TransformPointToMeshSpace(Vector2 input)
    {
        return new Vector3((input.y+_offset.x)*0.5f, 0f, input.x+_offset.y)*_scale;
    }
}
