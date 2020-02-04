using System.Collections.Generic;
using UnityEngine;

public class RoadNodeCollection
{
    private Dictionary<float, Dictionary<float, RoadNode>> _nodesDict
        = new Dictionary<float, Dictionary<float, RoadNode>>();

    public void AddPath(List<Vector2> points)
    {
        AddNode(points[0]);
        for(int i=1; i<points.Count; i++)
        {
            AddNode(points[i]);
            AddNeighbourRelation(points[i-1], points[i]);
        }
    }

    public List<RoadNode> BuildToList()
    {
        List<RoadNode> outList = new List<RoadNode>();
        foreach(Dictionary<float, RoadNode> nodeDict in _nodesDict.Values)
        {
            foreach(RoadNode node in nodeDict.Values)
            {
                outList.Add(node);
            }
        }
        return outList;
    }

    private void AddNode(Vector2 point)
    {
        if(!_nodesDict.ContainsKey(point.x))
            _nodesDict[point.x] = new Dictionary<float, RoadNode>();

        if(!_nodesDict[point.x].ContainsKey(point.y))
        {
            _nodesDict[point.x][point.y] = new RoadNode(point.x, point.y);
        }
    }

    private bool NodeExists(Vector2 point)
    {
        if(_nodesDict.ContainsKey(point.x) &&_nodesDict[point.x].ContainsKey(point.y))
            return true;
        return false;
    }

    private RoadNode GetNode(Vector2 point)
    {
        return _nodesDict[point.x][point.y];
    }

    private void AddNeighbourRelation(Vector2 point1, Vector2 point2)
    {
        if(NodeExists(point1) && NodeExists(point2))
        {
            RoadNode node1 = GetNode(point1);
            RoadNode node2 = GetNode(point2);
            node1.AddNeighbour(node2);
            node2.AddNeighbour(node1);
        }
        else
        {
            Debug.LogError("RoadNodeCollection tried to add a neighbour relation for two nodes that do not exist: "
                + point1 + ", " + point2);
        }
    }

}
