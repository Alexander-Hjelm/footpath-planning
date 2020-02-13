using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using GeoJSON;

public class GameManager : MonoBehaviour
{
    private string[] _highwayCategories = new string[]
    {
        "footpath",
        "residential",
        "secondary",
        "primary"
    };

    private RoadNodeCollection roadNodeCollection;
    private List<List<RoadNode>> roadNodesList;
    private Dictionary<RoadNode, RoadMesh> roadMeshes = new Dictionary<RoadNode, RoadMesh>();
    private RoadMesh roadMesh;

    void Start()
    {
        roadNodeCollection = new RoadNodeCollection();

        foreach(string hwy in _highwayCategories)
        {
            FeatureCollection collection = GeoJSONImporter.ReadFeatureCollectionFromFile("MapData/" + hwy);
            foreach(FeatureObject feature in collection.features)
            {
                List<Vector2> path = new List<Vector2>();
                List<PositionObject> positions = feature.geometry.AllPositions();
                foreach(PositionObject position in positions)
                {
                    path.Add(new Vector2(position.latitude, position.longitude));
                }
                roadNodeCollection.ReadPath(path, RoadNode.GetHighwayTypeFromString(hwy));
            }
        }
        roadNodesList = roadNodeCollection.BuildAndGetPaths();

        // Generate mesh
        GameObject roadMeshObj = new GameObject();
        roadMesh = roadMeshObj.AddComponent(typeof(RoadMesh)) as RoadMesh;
        roadMesh.GenerateMeshFromPaths(roadNodesList);
    }

}
