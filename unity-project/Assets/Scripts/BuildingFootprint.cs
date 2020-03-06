using System.Collections.Generic;
using UnityEngine;

public class BuildingFootprint
{
    private List<Vector3> _vertices = new List<Vector3>();

    public void AddVertex(Vector3 vertex)
    {
        _vertices.Add(vertex);
    }

    public List<Vector3> GetVertices()
    {
        return _vertices;
    }
}
