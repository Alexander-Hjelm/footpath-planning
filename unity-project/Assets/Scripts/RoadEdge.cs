using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RoadEdge
{
    private RoadNode _u;
    private RoadNode _v;

    public RoadEdge(RoadNode u, RoadNode v)
    {
        _u = u;
        _v = v;
    }

    public RoadNode GetU()
    {
        return _u;
    }

    public RoadNode GetV()
    {
        return _v;
    }
}
