using UnityEngine;
using GeoJSON;

public class GeoJSONImporter
{
    // Start is called before the first frame update
    public static FeatureCollection ReadFeatureCollectionFromFile(string path)
    {
        TextAsset encodedGeoJSON = Resources.Load(path) as TextAsset;
        FeatureCollection collection = GeoJSON.GeoJSONObject.Deserialize(encodedGeoJSON.text);
        return collection;
    }

}
