using System.Collections.Generic;
using UnityEngine;

public class RoadNodeCollection
{
    private Dictionary<float, Dictionary<float, RoadNode>> _readNodesByCoord
        = new Dictionary<float, Dictionary<float, RoadNode>>();

    private Queue<RoadPath> _readPaths = new Queue<RoadPath>();

    private Dictionary<RoadNode, int> _visitedCount = new Dictionary<RoadNode, int>();

    public void ReadPath(List<Vector2> points, RoadNode.HighwayType hwyType)
    {
        RoadPath path = new RoadPath(hwyType);
        for(int i=0; i<points.Count; i++)
        {
            // Cleanup, ignore all successive duplicate nodes in the paths
            if(i<points.Count-1
                && points[i].x == points[i+1].x
                && points[i].y == points[i+1].y)
            {
                continue;
            }

            // Generate and add the node
            RoadNode node = GetNode(points[i], hwyType);

            path.Add(node);
            BumpVisitedCount(node);
        }
        _readPaths.Enqueue(path);
    }

    public List<RoadPath> BuildAndGetPaths()
    {
        Queue<RoadPath> tentativePaths = _readPaths;
        List<RoadPath> outPaths = new List<RoadPath>();

        int crash_safe = 0;
        while(tentativePaths.Count > 0)
        {
            RoadPath path = tentativePaths.Dequeue();
            
            for(int i=0; i<path.Count(); i++)
            {
                RoadNode node = path.Get(i);

                if(i>0 && i<path.Count()-1 && _visitedCount[node] > 1)
                {
                    // This is an intersection, we should split the path
                    RoadPath path2 = new RoadPath(path.GetHighwayType());
                    for(int j=0; j<i; j++)
                    {
                        // Move all other points from the first path to the second
                        path2.Add(path.Get(0));
                        path.RemoveAt(0);
                    }
                    path2.Add(node); // Finally add the intersection point
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
        {
            _readNodesByCoord[point.x] = new Dictionary<float, RoadNode>();
        }

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
            // Node has now been read more than once, therefore mark it as an intersection
            _readNodesByCoord[point.x][point.y].SetIntersection();
            return _readNodesByCoord[point.x][point.y];
        }
        else
        {
            return AddAndReturnNode(point, hwyType);
        }
    }

}
