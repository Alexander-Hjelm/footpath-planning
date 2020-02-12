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

    void Update()
    {
        // Debug lines
        /*
        foreach(List<RoadNode> path in roadNodesList)
        {
            for(int i=0; i<path.Count-1; i++)
            {
                RoadNode a = path[i];
                RoadNode b = path[i+1];
                Vector3 start = new Vector3((a.GetY()-18.05f)*0.5f, 0f, a.GetX()-59.34f)*50f;
                Vector3 stop = new Vector3((b.GetY()-18.05f)*0.5f, 0f, b.GetX()-59.34f)*50f;
                Debug.DrawLine(start, stop);
            }
        }
        */
        //Debug.Log(roadMesh.GetMesh().vertices[roadMesh.GetMesh().vertices.Length-1]);
        Debug.Log(roadMesh.GetMesh().triangles[roadMesh.GetMesh().triangles.Length-1]);
    }

}
