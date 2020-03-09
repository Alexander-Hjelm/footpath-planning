using System.Collections.Generic;
using UnityEngine;

public class RoadPath
{
    private List<RoadNode> _nodes;
    private RoadNode.HighwayType _highwayType;
    private string _id;

    public RoadPath(RoadNode.HighwayType highwayType, string id)
    {
        _nodes = new List<RoadNode>();
        _highwayType = highwayType;
        _id = id;
    }

    public RoadNode.HighwayType GetHighwayType()
    {
        return _highwayType;
    }

    public string GetId()
    {
        return _id;
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
