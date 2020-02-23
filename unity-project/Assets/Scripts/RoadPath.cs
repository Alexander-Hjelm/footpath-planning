using System.Collections.Generic;
using UnityEngine;

public class RoadPath
{
    private List<RoadNode> _nodes;
    private RoadNode.HighwayType _highwayType;

    public RoadPath(RoadNode.HighwayType highwayType)
    {
        _nodes = new List<RoadNode>();
        _highwayType = highwayType;
    }

    public RoadNode.HighwayType GetHighwayType()
    {
        return _highwayType;
    }

    public void Add(RoadNode node)
    {
        _nodes.Add(node);
    }

    public RoadNode Get(int i)
    {
        return _nodes[i];
    }

    public int Count()
    {
        return _nodes.Count;
    }

    public void RemoveAt(int i)
    {
        _nodes.RemoveAt(i);
    }
}
