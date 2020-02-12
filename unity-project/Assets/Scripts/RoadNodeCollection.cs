using System.Collections.Generic;
using UnityEngine;

public class RoadNodeCollection
{
    private Dictionary<float, Dictionary<float, RoadNode>> _readNodesByCoord
        = new Dictionary<float, Dictionary<float, RoadNode>>();

    private Queue<List<RoadNode>> _readPaths = new Queue<List<RoadNode>>();

    private Dictionary<RoadNode, int> _visitedCount = new Dictionary<RoadNode, int>();

    public void ReadPath(List<Vector2> points, RoadNode.HighwayType hwyType)
    {
        List<RoadNode> path = new List<RoadNode>();
        for(int i=1; i<points.Count; i++)
        {
            RoadNode node = GetNode(points[i], hwyType);
            path.Add(node);
            BumpVisitedCount(node);
        }
        _readPaths.Enqueue(path);
    }

    public List<List<RoadNode>> BuildAndGetPaths()
    {
        Queue<List<RoadNode>> tentativePaths = _readPaths;
        List<List<RoadNode>> outPaths = new List<List<RoadNode>>();

        int crash_safe = 0;
        while(tentativePaths.Count > 0)
        {
            List<RoadNode> path = tentativePaths.Dequeue();
            
            for(int i=0; i<path.Count; i++)
            {
                RoadNode node = path[i];
                if(i>0 && i<path.Count-1 && _visitedCount[node] > 1)
                {
                    // This is an intersection, we should split the path
                    List<RoadNode> path2 = new List<RoadNode>();
                    path2.Add(node); // First add the intersection point
                    for(int j=i+1; j<path.Count; j++)
                    {
                        // Move all other points from the first path to the second
                        path2.Add(path[j]);
                        path.RemoveAt(j);
                    }
                    // Queue the new path, deal with it in a later iteration
                    tentativePaths.Enqueue(path2);
                    break;
                }
            }
            
            outPaths.Add(path);

            crash_safe++;
            if (crash_safe > 7000)
            {
                Debug.Log("Crashed with " + tentativePaths.Count + " paths remaining");
                break;
            }
        }

        return outPaths;
    }

    private void BumpVisitedCount(RoadNode node)
    {
        if(_visitedCount.ContainsKey(node))
        {
            _visitedCount[node]++;
        }
        else
        {
            _visitedCount[node] = 0;
        }
    }

    private RoadNode AddAndReturnNode(Vector2 point, RoadNode.HighwayType hwyType)
    {
        if(!_readNodesByCoord.ContainsKey(point.x))
            _readNodesByCoord[point.x] = new Dictionary<float, RoadNode>();

        if(!_readNodesByCoord[point.x].ContainsKey(point.y))
        {
            _readNodesByCoord[point.x][point.y] = new RoadNode(point.x, point.y, hwyType);
        }
        return _readNodesByCoord[point.x][point.y];
    }

    private bool NodeHasBeenRead(Vector2 point)
    {
        if(_readNodesByCoord.ContainsKey(point.x) && _readNodesByCoord[point.x].ContainsKey(point.y))
            return true;
        return false;
    }

    private RoadNode GetNode(Vector2 point, RoadNode.HighwayType hwyType)
    {
        if(NodeHasBeenRead(point))
        {
            return _readNodesByCoord[point.x][point.y];
        }
        else
        {
            return AddAndReturnNode(point, hwyType);
        }
    }
/*
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
    */

}
