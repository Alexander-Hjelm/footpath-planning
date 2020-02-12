using System.Collections;
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
    private float _scale = 500f;
    float _roadWidth = 11f;
    private Vector2 _offset = new Vector2(-18.05f, -59.34f);

    public void Awake()
    {
        MeshRenderer meshRenderer = gameObject.AddComponent(typeof(MeshRenderer)) as MeshRenderer;
        Material material = new Material(Shader.Find("Standard"));
        material.mainTexture = Resources.Load("Textures/Road") as Texture;
        meshRenderer.sharedMaterial = material;
        _meshFilter = gameObject.AddComponent(typeof(MeshFilter)) as MeshFilter;

    }

    public void GenerateMeshFromPaths(List<List<RoadNode>> paths)
    {
        Mesh mesh = new Mesh();

        List<Vector3> vertices = new List<Vector3>();
        List<Vector2> uvs = new List<Vector2>();
        List<int> triangles = new List<int>();
        int countedVertices = 0;
        Dictionary<RoadNode, List<RoadEndPoint>> intersectionNodes = new Dictionary<RoadNode, List<RoadEndPoint>>();
        foreach(List<RoadNode> path in paths)
        {
            RoadEndPoint previousRoadEndPoint = new RoadEndPoint(Vector3.zero, Vector3.zero, -1, -1, Vector3.zero);

            RoadNode.HighwayType hwyType = RoadNode.HighwayType.NONE;

            for(int i=0; i<path.Count-1; i++)
            {
                RoadNode a = path[i];
                RoadNode b = path[i+1];
                // Get hwy type from the second node in the path, since the intersection may be of another type
                if(hwyType == RoadNode.HighwayType.NONE) hwyType = b.GetHighwayType();
                Vector3 posA = TransformPointToMeshSpace(a.GetPosAsVector2());
                Vector3 posB = TransformPointToMeshSpace(b.GetPosAsVector2());
                Vector3 tangent = (posB - posA).normalized;
                if(tangent == Vector3.zero)
                {
                    // TODO: Tangets should not be zero, examine why this happens earlier in the pipeline
                    Debug.LogError("Tangent is zero!");
                }
                Vector3 normal = new Vector3(tangent.z, 0f, -tangent.x)*0.001f;

                Vector3 leftStartPoint = posA + normal*_roadWidth;
                Vector3 rightStartPoint = posA - normal*_roadWidth;
                Vector3 leftEndPoint = posB + normal*_roadWidth;
                Vector3 rightEndPoint = posB - normal*_roadWidth;

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
                float uvXOffset = 0f;
                switch(hwyType)
                {
                    case RoadNode.HighwayType.FOOTPATH:
                        uvXOffset = 0.75f;
                        break;
                    case RoadNode.HighwayType.RESIDENTIAL:
                        uvXOffset = 0.5f;
                        break;
                    case RoadNode.HighwayType.SECONDARY:
                        uvXOffset = 0.25f;
                        break;
                    case RoadNode.HighwayType.PRIMARY:
                        uvXOffset = 0f;
                        break;
                }

                uvs.Add(new Vector2(uvXOffset+0.25f, 0f) * uvScale);
                uvs.Add(new Vector2(uvXOffset, 0f) * uvScale);
                uvs.Add(new Vector2(uvXOffset+0.25f, 1f) * uvScale);
                uvs.Add(new Vector2(uvXOffset, 1f) * uvScale);

                // Set the last end point for the next path segment
                previousRoadEndPoint = new RoadEndPoint(leftEndPoint, rightEndPoint, vertices.Count-2, vertices.Count-1, tangent);

                // If this is the beginning or end nod of the path, store it as an intersection candidate
                if(i==0)
                {
                    if(!intersectionNodes.ContainsKey(a))
                    {
                        intersectionNodes[a] = new List<RoadEndPoint>();
                    }
                    intersectionNodes[a].Add(new RoadEndPoint(leftStartPoint, rightStartPoint, vertices.Count-4, vertices.Count-3, tangent));
                }
                else if(i==path.Count-2)
                {
                    if(!intersectionNodes.ContainsKey(b))
                    {
                        intersectionNodes[b] = new List<RoadEndPoint>();
                    }
                    intersectionNodes[b].Add(new RoadEndPoint(leftEndPoint, rightEndPoint, vertices.Count-2, vertices.Count-1, tangent));
                }
            }
        }

        // Intersections
        foreach(RoadNode node in intersectionNodes.Keys)
        {
            List<RoadEndPoint> endPoints = intersectionNodes[node];
            //TODO: Should work for intersections with 2 nodes as well
            if(endPoints.Count < 2)
            {
                // Skip the node if it has less than three end points. Then it is not an intersection
                continue;
            }

            // Order the end points by angle
            RoadEndPoint[] endPointsSorted = endPoints.OrderBy(v => Vector3.Angle(v.tangent, Vector3.right)).ToArray();

            List<int> storedIntersectionIndices = new List<int>();

            // Midpoint of the intersection
            Vector3 midPoint = Vector3.zero;

            // Now the end points are sorted, get them one by one
            for(int i=0; i<endPointsSorted.Length; i++)
            {

                RoadEndPoint a = endPointsSorted[i];
                RoadEndPoint b = endPointsSorted[(i+1)%endPointsSorted.Length];

                midPoint += (a.rightPoint + a.leftPoint)/2;
                
                // Get the intersection point
                // Get the right pos from end point 1 and left pos from end point 2
                Vector3 intersection;
                bool intersectionWasSet = false;
                if(MathUtils.LineLineIntersection(out intersection, a.rightPoint, a.tangent,
                    b.leftPoint, b.tangent))
                {
                    intersectionWasSet = true;
                }
                else if((a.tangent + b.tangent).magnitude < 0.01f)
                {
                    // tangents are opposite, pick the middle point
                    intersection = (a.rightPoint + b.leftPoint)/2;
                    intersectionWasSet = true;
                }
                else if((a.tangent - b.tangent).magnitude < 0.01f)
                {
                    // tangents are the same. This happens due to direty data, but pick the middle point for now
                    intersection = (a.rightPoint + b.leftPoint)/2;
                    intersectionWasSet = true;
                }

                if(intersectionWasSet)
                {
                    // Get the vertex indices of the end points and move them to the new intersection points
                    vertices[a.rightIndex] = intersection;
                    vertices[b.leftIndex] = intersection;
                    
                    storedIntersectionIndices.Add(vertices.Count-1);
                    continue;
                }
                else
                {
                    Debug.LogError("Found an intersection with two incoming paths that have the same tangents! " + a.tangent + ", " + b.tangent + ". a.right = " + a.rightPoint + ", b.left = " + b.leftPoint);
                    Debug.LogError(a.tangent.x + b.tangent.x);
                }
            }

            // Divide the midpoint to obtain the average
            midPoint /= endPointsSorted.Length;

            // Add the midpoint of the intersection as the next vertex
            vertices.Add(midPoint);
            uvs.Add(new Vector2(0.5f, 0.5f));

            for(int i=0; i< storedIntersectionIndices.Count; i++)
            {
                // Create new triangles, stitch all the vertices together
                triangles.Add(storedIntersectionIndices[i]);
                triangles.Add(storedIntersectionIndices[(i+1)%storedIntersectionIndices.Count]);
                triangles.Add(vertices.Count-1); //Finally the midpoint, last in the vertex array
            }

        }
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

        _meshFilter.mesh = mesh;
    }

    private Vector3 TransformPointToMeshSpace(Vector2 input)
    {
        return new Vector3((input.y+_offset.x)*0.5f, 0f, input.x+_offset.y)*_scale;
    }
}
