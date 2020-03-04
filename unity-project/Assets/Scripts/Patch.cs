using System.Collections.Generic;
using UnityEngine;

public class Patch
{
    public struct Edge
    {
        public int IndexU;
        public int IndexV;

        public Edge(int indexU, int indexV)
        {
            IndexU = indexU;
            IndexV = indexV;
        }
    }

    private Vector2[] _vertices;
    private Edge[] _edges;
    private Dictionary<string, float> _statistics = new Dictionary<string, float>();

    public Patch(PatchData patchData)
    {
        _vertices = new Vector2[patchData.points.GetLength(0)];
        for(int i=0; i<patchData.points.GetLength(0); i++)
        {
            float x = patchData.points[i, 0];
            float y = patchData.points[i, 1];
            _vertices[i] = new Vector2(x, y);
        }
        _edges = new Edge[patchData.edges.GetLength(0)];
        for(int i=0; i<patchData.edges.GetLength(0); i++)
        {
            int u = patchData.edges[i, 0];
            int v = patchData.edges[i, 1];
            _edges[i] = new Edge(u, v);
        }

        _statistics["avg_len"] = patchData.stat_avg_len;
        _statistics["var_len"] = patchData.stat_var_len;
        _statistics["avg_curv"] = patchData.stat_avg_curv;
        _statistics["var_curv"] = patchData.stat_var_curv;
    }

    public Vector2[] GetVertices()
    {
        return _vertices;
    }

    public Edge[] GetEdges()
    {
        return _edges;
    }

    public float GetStatistic(string label)
    {
        return _statistics[label];
    }
}
