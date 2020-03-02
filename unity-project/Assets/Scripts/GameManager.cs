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
    private Dictionary<RoadNode.HighwayType, Patch[]> _loadedPatches = new Dictionary<RoadNode.HighwayType, Patch[]>();

    private bool _debugRawPaths = false;
    private bool _debugPatches = true;

    private static GameManager _instance;

    private void Awake()
    {
        _instance = this;
    }

    private void Start()
    {
        // Read patch data
        foreach(string hwy in _highwayCategories)
        {
            PatchData[] patchData = JsonManager.ReadObject<PatchData[]>("Assets/Resources/PatchData/" + hwy);
            Patch[] patches = new Patch[patchData.Length]; 
            for(int i=0; i<patchData.Length; i++)
            {
                patches[i] = new Patch(patchData[i]);
            }
            _loadedPatches[RoadNode.GetHighwayTypeFromString(hwy)] = patches;
        }

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
                        RoadMesh.TransformPointToMeshSpaceAxisFlipped(path[j]),
                        RoadMesh.TransformPointToMeshSpaceAxisFlipped(path[j+1]));
                }
            }
        }

        if(_debugPatches)
        {
            foreach(RoadNode.HighwayType hwyType in _loadedPatches.Keys)
            {
                foreach(Patch patch in _loadedPatches[hwyType])
                {
                    Vector2[] vertices = patch.GetVertices();
                    Patch.Edge[] edges = patch.GetEdges();
                    foreach(Patch.Edge edge in edges)
                    {
                        Vector2 u = vertices[edge.IndexU];
                        Vector2 v = vertices[edge.IndexV];
                        Debug.DrawLine(
                            RoadMesh.TransformPointToMeshSpace(u),
                            RoadMesh.TransformPointToMeshSpace(v));
                    }
                }
            }
        }
    }

    public static List<RoadPath> GetPaths()
    {
        return _instance.roadNodesList;
    }

}
