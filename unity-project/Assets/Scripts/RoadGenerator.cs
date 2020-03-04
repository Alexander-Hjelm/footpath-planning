using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RoadGenerator
{
    private static Dictionary<RoadNode.HighwayType, Patch[]> _loadedPatches = new Dictionary<RoadNode.HighwayType, Patch[]>();

    public static void LoadPatches(Dictionary<RoadNode.HighwayType, Patch[]> loadedPatches)
    {
        _loadedPatches = loadedPatches;
    }

    public static void PopulatePolygonFromExamplePatches(List<RoadPath> paths, Polygon polygon)
    {
        if(_loadedPatches.Count == 0)
        {
            Debug.LogError("Tried to call PopulatePolygonFromExamplePatches(), but the loaded patches dataset is empty!");
            return;
        }

        // Queue all nodes that are inside the polygon
        Queue<RoadNode> tentativeNodes = new Queue<RoadNode>();
        List<RoadNode> hitNodes = new List<RoadNode>();
        foreach(RoadPath path in paths)
        {
            for(int i=0; i<path.Count(); i++)
            {
                RoadNode node = path.Get(i);
                if(!hitNodes.Contains(node))
                {
                    hitNodes.Add(node);
                    if(polygon.ContainsPoint(node.GetPosAsVector2()))
                    {
                        tentativeNodes.Enqueue(node);
                    }
                }
            }
        }

        // If no points were found, queue the polygon centroid
        if(tentativeNodes.Count == 0)
        {
            tentativeNodes.Enqueue(new RoadNode(polygon.GetCenter(), RoadNode.HighwayType.SECONDARY));
        }


        // Finally, Notify the GameManager to generate a new mesh
        GameManager.SetPaths(paths);
        GameManager.GenerateMesh();
    }

    private static void AddPatch(Patch patch, RoadNode anchorNode)
    {
        throw new System.NotImplementedException();
    }

    private static bool CollisionCheck(Patch patch, List<RoadEdge> edges)
    {
        // Do a collision check between all edges in a patch and a set of edges
        foreach(Patch.Edge patchEdge in patch.GetEdges())
        {
            foreach(RoadEdge placedEdge in edges)
            {
                if(CollisionCheck(patch.GetVertices()[patchEdge.IndexU], patch.GetVertices()[patchEdge.IndexV], edges))
                {
                    return true;
                }
            }
        }
        return false;
    }

    private static bool CollisionCheck(RoadNode a, RoadNode b, List<RoadEdge> edges)
    {
        // Do a collision check between a node pair and a set of edges
        return CollisionCheck(a.GetPosAsVector2(), b.GetPosAsVector2(), edges);
    }

    private static bool CollisionCheck(Vector2 a, Vector2 b, List<RoadEdge> edges)
    {
        // Do a collision check between an edge (poisition pair) and a set of edges
        foreach(RoadEdge edge in edges)
        {
            Vector3 intersection;
            if(MathUtils.LineSegmentLineSegmentIntersection(out intersection, a, b, edge.GetU().GetPosAsVector2(), edge.GetV().GetPosAsVector2()))
            {
                return true;
            }
        }
        return false;
    }
}
