using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RoadMesh : MonoBehaviour
{
    private MeshFilter _meshFilter;

    public void Awake()
    {
        _meshFilter = gameObject.AddComponent(typeof(MeshFilter)) as MeshFilter;
        gameObject.AddComponent(typeof(MeshRenderer));
    }

    public void GenerateMeshFromPoints(List<Vector2> points)
    {
        Mesh mesh = new Mesh();
        GetComponent<MeshFilter>().mesh = mesh;
        //mesh.vertices = newVertices;
        //mesh.uv = newUV;
        //mesh.triangles = newTriangles;
    }
}
