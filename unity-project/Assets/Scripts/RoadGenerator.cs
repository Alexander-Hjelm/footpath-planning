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
        List<RoadEdge> edgesForCollisionCheck = new List<RoadEdge>();
        foreach(RoadPath path in paths)
        {
            for(int i=0; i<path.Count(); i++)
            {
                RoadNode node = path.Get(i);
                if(polygon.ContainsPoint(node.GetPosAsVector2()))
                {
                    if(!hitNodes.Contains(node))
                    {
                        tentativeNodes.Enqueue(node);
                    }

                    // Add a new edge to run collision checks with later
                    // This handles the cases where the current node is inside to polygon and the next one is either inside or outside it
                    if(i<path.Count()-1)
                    {
                        edgesForCollisionCheck.Add(new RoadEdge(node, path.Get(i+1)));
                    }
                }
                else
                {
                    // Add a new edge to run collision checks with later
                    // This handles the cases where the current node is outside to polygon but the next one is inside it
                    if(i<path.Count()-1)
                    {
                        RoadNode next = path.Get(i+1);
                        if(polygon.ContainsPoint(next.GetPosAsVector2()))
                        {
                            edgesForCollisionCheck.Add(new RoadEdge(node, next));
                        }
                    }
                }
                hitNodes.Add(node);
            }
        }

        // If no points were found, queue the polygon centroid
        if(tentativeNodes.Count == 0)
        {
            tentativeNodes.Enqueue(new RoadNode(polygon.GetCenter(), RoadNode.HighwayType.RESIDENTIAL));
        }

        while(tentativeNodes.Count > 0)
        {
            RoadNode anchorNode = tentativeNodes.Dequeue();
            foreach(Patch patch in _loadedPatches[anchorNode.GetHighwayType()])
            {
                List<RoadNode> patchEndPoints = new List<RoadNode>();
                if(TryAddPatch(out patchEndPoints, patch, anchorNode, polygon, edgesForCollisionCheck, paths))
                {
                    // Queue end points to the tentative queue
                    foreach(RoadNode endPoint in patchEndPoints)
                    {
                        //TODO: Enable this line as soon as the collision check works
                        //tentativeNodes.Queue(endPoint);
                    }
                    
                    break;
                }
            }
        }

        // Finally, Notify the GameManager to generate a new mesh
        GameManager.SetPaths(paths);
        GameManager.GenerateMesh();
    }

    private static bool TryAddPatch(out List<RoadNode> endNodes, Patch patch, RoadNode anchorNode, Polygon polygon, List<RoadEdge> edgesForCollisionCheck, List<RoadPath> pathsToBeAddedTo)
    {
        endNodes = new List<RoadNode>();

        // Select the first node in the patch as the patch-side anchor point
        // TODO: Make a better selection function
        Vector2 patchsideAnchor = patch.GetVertices()[0];
        Vector2 patchOffset = anchorNode.GetPosAsVector2()-patchsideAnchor;

        // Check that all points in the patch are inside the polygon
        foreach(Vector2 v in patch.GetVertices())
        {
            if(!polygon.ContainsPoint(v))
                return false;
        }

        // Check that no edges in the patch intersect with any existing edges
        if(CollisionCheck(patch, edgesForCollisionCheck, patchOffset))
        {
            return false;
        }

        // Go over all nodes in the patches and add them to the paths, anchor position factored in
        // Add a new path for every edge in the patch
        // TODO: Generate the unique nodes first, then link them together in paths
        foreach(Patch.Edge edge in patch.GetEdges())
        {
            Vector2 u = patch.GetVertices()[edge.IndexU] + patchOffset;
            Vector2 v = patch.GetVertices()[edge.IndexV] + patchOffset;

            RoadNode nodeU = new RoadNode(u, anchorNode.GetHighwayType());
            RoadNode nodeV = new RoadNode(v, anchorNode.GetHighwayType());

            RoadPath path = new RoadPath(anchorNode.GetHighwayType());
            path.Add(nodeU);
            path.Add(nodeV);

            pathsToBeAddedTo.Add(path);

            if(patch.IsVertexEndPoint(edge.IndexU))
                endNodes.Add(nodeU);
            if(patch.IsVertexEndPoint(edge.IndexV))
                endNodes.Add(nodeV);
        }
        return true;
    }

    private static bool CollisionCheck(Patch patch, List<RoadEdge> edges, Vector2 anchorOffset)
    {
        // Do a collision check between all edges in a patch and a set of edges
        foreach(Patch.Edge patchEdge in patch.GetEdges())
        {
            foreach(RoadEdge placedEdge in edges)
            {
                if(CollisionCheck(patch.GetVertices()[patchEdge.IndexU] + anchorOffset, patch.GetVertices()[patchEdge.IndexV] + anchorOffset, edges))
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
