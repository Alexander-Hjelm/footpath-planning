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
        
    }
}
