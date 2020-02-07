using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class RoadMesh : MonoBehaviour
{
    private MeshFilter _meshFilter;

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
        foreach(List<RoadNode> path in paths)
        {
            for(int i=0; i<path.Count-1; i++)
            {
                RoadNode a = path[i];
                RoadNode b = path[i+1];
                Vector2 posA2D = a.GetPosAsVector2();
                Vector3 posA = new Vector3((posA2D.y-18.05f)*0.5f, 0f, posA2D.x-59.34f)*20f;
                Vector2 posB2D = b.GetPosAsVector2();
                Vector3 posB = new Vector3((posB2D.y-18.05f)*0.5f, 0f, posB2D.x-59.34f)*20f;
                Vector3 tangent = posB - posA;
                Vector3 normal = new Vector3(tangent.z, 0f, -tangent.x);
                vertices.Add(posA + normal*roadWidth);
                vertices.Add(posA - normal*roadWidth);
                vertices.Add(posB + normal*roadWidth);
                vertices.Add(posB - normal*roadWidth);
                triangles.Add(countedVertices);
                triangles.Add(countedVertices+1);
                triangles.Add(countedVertices+2);
                triangles.Add(countedVertices+1);
                triangles.Add(countedVertices+2);
                triangles.Add(countedVertices+3);
                countedVertices += 4;
            }
        }

        mesh.vertices = vertices.ToArray();
        mesh.triangles = triangles.ToArray();
        Debug.Log(mesh.triangles.Count());
        //mesh.uv = newUV;
        
        _meshFilter.mesh = mesh;
    }
}
