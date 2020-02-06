using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class RoadMesh : MonoBehaviour
{
    private MeshFilter _meshFilter;

    public void Awake()
    {
        _meshFilter = gameObject.AddComponent(typeof(MeshFilter)) as MeshFilter;
        gameObject.AddComponent(typeof(MeshRenderer));
    }

    public void GenerateMeshFromPaths(List<List<RoadNode>> paths)
    {
        Mesh mesh = new Mesh();
        GetComponent<MeshFilter>().mesh = mesh;
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
                Vector2 posA = a.GetPosAsVector2();
                Vector2 posB = b.GetPosAsVector2();
                Vector2 tangent = posB - posA;
                Vector2 normal = new Vector2(tangent.y, -tangent.x);
                vertices.Add((Vector3)(posA + tangent*roadWidth));
                vertices.Add((Vector3)(posA - tangent*roadWidth));
                vertices.Add((Vector3)(posB + tangent*roadWidth));
                vertices.Add((Vector3)(posB - tangent*roadWidth));
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
    }
}
