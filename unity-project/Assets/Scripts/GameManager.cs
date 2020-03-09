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
    private List<BuildingFootprint> buildingFootprintList = new List<BuildingFootprint>();
    private Dictionary<RoadNode, RoadMesh> roadMeshes = new Dictionary<RoadNode, RoadMesh>();
    private RoadMesh roadMesh;
    private BuildingMesh buildingMesh;
    private List<List<Vector2>> rawPaths = new List<List<Vector2>>();
    private Dictionary<RoadNode.HighwayType, Patch[]> _loadedPatches = new Dictionary<RoadNode.HighwayType, Patch[]>();
    private Dictionary<string, float> _pathWidths;

    private bool _debugRawPaths = false;
    private bool _debugPatches = false;
    private bool _debugOnlyResidential = false;

    private static GameManager _instance;

    private void Awake()
    {
        _instance = this;
    }

    private void Start()
    {
        if(_debugOnlyResidential)
        {
            _highwayCategories = new string[]{"residential"};
        }

        // Read patch data
        foreach(string hwy in _highwayCategories)
        {
            PatchData[] patchData = JsonManager.ReadObject<PatchData[]>("Assets/Resources/PatchData/" + hwy);

            // Coordinate transformation
            foreach(PatchData pd in patchData)
            {
                float[,] points = pd.points;
                for(int i=0; i<points.GetLength(0); i++)
                {
                    float x = points[i, 0];
                    float y = points[i, 1];
                    Vector3 transformed = RoadMesh.TransformPointToMeshSpace(new Vector2(x, y));
                    points[i, 0] = transformed.x;
                    points[i, 1] = transformed.z;
                }
            }
            
            // Create patches
            Patch[] patches = new Patch[patchData.Length]; 
            for(int i=0; i<patchData.Length; i++)
            {
                patches[i] = new Patch(patchData[i]);
            }
            _loadedPatches[RoadNode.GetHighwayTypeFromString(hwy)] = patches;
        }

        // Read building footprint data
        FeatureCollection buildingFeatureCollection = GeoJSONImporter.ReadFeatureCollectionFromFile("MapData/buildings");
        foreach(FeatureObject feature in buildingFeatureCollection.features)
        {
            BuildingFootprint buildingFootprint = new BuildingFootprint();
            GeometryObject geometryObject = feature.geometry;
            List<PositionObject> positions = geometryObject.AllPositions();
            foreach(PositionObject position in positions)
            {
                // Coordinate transformation
                Vector3 transformed = RoadMesh.TransformPointToMeshSpace(new Vector2(position.longitude, position.latitude));
                // Add node to path
                buildingFootprint.AddVertex(transformed);
            }
            buildingFootprintList.Add(buildingFootprint);
        }

        // Read paths widths
        _pathWidths = JsonManager.ReadObject<Dictionary<string, float>>("Assets/Resources/MapData/path_widths");

        // Send a reference of the loaded paths to the RoadGenerator
        RoadGenerator.LoadPatches(_loadedPatches);

        roadNodeCollection = new RoadNodeCollection();

        // Read paths
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
                    // Coordinate transformation
                    Vector3 transformed = RoadMesh.TransformPointToMeshSpace(new Vector2(position.longitude, position.latitude));

                    // Add node to path
                    path.Add(new Vector2(transformed.x, transformed.z));
                }
                roadNodeCollection.ReadPath(path, RoadNode.GetHighwayTypeFromString(hwy), feature.properties["@id"]);
                rawPaths.Add(path);
            }
        }
        roadNodesList = roadNodeCollection.BuildAndGetPaths();

        GenerateRoadMesh();
        GenerateBuildingMesh();
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
                        new Vector3(path[j].x, 0f, path[j].y),
                        new Vector3(path[j+1].x, 0f, path[j+1].y));
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
                            new Vector3(u.x, 0f, u.y),
                            new Vector3(v.x, 0f, v.y));
                    }
                }
            }
        }
    }

    public static void GenerateRoadMesh()
    {
        if(_instance.roadMesh != null)
        {
            DestroyImmediate(_instance.roadMesh.gameObject);
        }

        // Generate mesh
        GameObject roadMeshObj = new GameObject();
        _instance.roadMesh = roadMeshObj.AddComponent(typeof(RoadMesh)) as RoadMesh;
        _instance.roadMesh.GenerateMeshFromPaths(_instance.roadNodesList, _instance._pathWidths);
    }

    public static void GenerateBuildingMesh()
    {
        if(_instance.buildingMesh != null)
        {
            DestroyImmediate(_instance.buildingMesh.gameObject);
        }

        // Generate mesh
        GameObject buildingMeshObj = new GameObject();
        _instance.buildingMesh = buildingMeshObj.AddComponent(typeof(BuildingMesh)) as BuildingMesh;
        _instance.buildingMesh.GenerateMeshFromFootprints(_instance.buildingFootprintList);
    }

    public static List<RoadPath> GetPaths()
    {
        return _instance.roadNodesList;
    }

    public static void SetPaths(List<RoadPath> paths)
    {
        _instance.roadNodesList = paths;
    }

}
