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
    private List<RoadPath> roadNodesList;
    private Dictionary<RoadNode, RoadMesh> roadMeshes = new Dictionary<RoadNode, RoadMesh>();
    private RoadMesh roadMesh;
    private List<List<Vector2>> rawPaths = new List<List<Vector2>>();
    private bool _debugRawPaths = true;

    void Start()
    {
        roadNodeCollection = new RoadNodeCollection();

        foreach(string hwy in _highwayCategories)
        {
            FeatureCollection collection = GeoJSONImporter.ReadFeatureCollectionFromFile("MapData/" + hwy);
            foreach(FeatureObject feature in collection.features)
            {
                List<Vector2> path = new List<Vector2>();
                GeometryObject geometryObject = feature.geometry;

                // Don't treat polygon objects, just skip them
                if(geometryObject as PolygonGeometryObject != null
                        || geometryObject as MultiPolygonGeometryObject != null)
                {
                    continue;
                }

                List<PositionObject> positions = geometryObject.AllPositions();
                foreach(PositionObject position in positions)
                {
                    path.Add(new Vector2(position.latitude, position.longitude));
                }
                roadNodeCollection.ReadPath(path, RoadNode.GetHighwayTypeFromString(hwy));
                rawPaths.Add(path);
            }
        }
        roadNodesList = roadNodeCollection.BuildAndGetPaths();

        // Generate mesh
        GameObject roadMeshObj = new GameObject();
        roadMesh = roadMeshObj.AddComponent(typeof(RoadMesh)) as RoadMesh;
        roadMesh.GenerateMeshFromPaths(roadNodesList);
    }

    private void Update()
    {
        if(_debugRawPaths)
        {
            for(int i=0; i<rawPaths.Count; i++)
            {
                List<Vector2> path = rawPaths[i];
                for(int j=0; j<path.Count-1; j++)
                {
                    Debug.DrawLine(
                        RoadMesh.TransformPointToMeshSpace(path[j]),
                        RoadMesh.TransformPointToMeshSpace(path[j+1]));
                }
            }
        }
    }

}
