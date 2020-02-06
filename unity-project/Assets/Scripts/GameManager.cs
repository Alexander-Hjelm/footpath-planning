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
                roadNodeCollection.ReadPath(path);
            }
        }
        roadNodesList = roadNodeCollection.BuildAndGetPaths();

        // Generate meshes and store them
        //foreach(RoadNode node in roadNodesList)
        //{
            //GameObject roadMeshObj = new GameObject();
            //RoadMesh roadMesh = roadMeshObj.AddComponent(typeof(RoadMesh)) as RoadMesh;
            // TODO: Add more points here, go through all neighbours as long as there are only 2 for every node
            // That way we can generate all simple roads
            //roadMesh.GenerateMeshFromPoints(new List<Vector2>() {node.GetPosAsVector2()});
            //roadMeshes[node] = roadMesh;
        //}
    }

    void Update()
    {
        //RoadNode c = roadNodesList[0];
        foreach(List<RoadNode> path in roadNodesList)
        {
            for(int i=0; i<path.Count-1; i++)
            {
                RoadNode a = path[i];
                RoadNode b = path[i+1];
                Vector3 start = new Vector3((a.GetY()-18.05f)*0.5f, 0f, a.GetX()-59.34f)*20f;
                Vector3 stop = new Vector3((b.GetY()-18.05f)*0.5f, 0f, b.GetX()-59.34f)*20f;
                Debug.DrawLine(start, stop);
            }
        }
    }

}
