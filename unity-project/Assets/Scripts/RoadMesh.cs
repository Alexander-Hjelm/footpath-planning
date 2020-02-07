using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class RoadMesh : MonoBehaviour
{
    private MeshFilter _meshFilter;
    private float _scale = 20f;
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
        foreach(List<RoadNode> path in paths)
        {
            for(int i=0; i<path.Count-1; i++)
            {
                RoadNode a = path[i];
                RoadNode b = path[i+1];
                Vector3 posA = TransformPointToMeshSpace(a.GetPosAsVector2());
                Vector3 posB = TransformPointToMeshSpace(b.GetPosAsVector2());
                Vector3 tangent = posB - posA;
                Vector3 normal = new Vector3(tangent.z, 0f, -tangent.x).normalized*0.001f;
                vertices.Add(posA + normal*roadWidth);
                vertices.Add(posA - normal*roadWidth);
                vertices.Add(posB + normal*roadWidth);
                vertices.Add(posB - normal*roadWidth);
                triangles.Add(countedVertices);
                triangles.Add(countedVertices+1);
                triangles.Add(countedVertices+2);
                triangles.Add(countedVertices+3);
                triangles.Add(countedVertices+2);
                triangles.Add(countedVertices+1);
                countedVertices += 4;
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
