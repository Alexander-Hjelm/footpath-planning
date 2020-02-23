using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class MapDebugHelper : MonoBehaviour
{
    private static double targetNodeX = 6.144524;
    private static double targetNodeY = -7.995605;

    [SerializeField] private InputField _coordXText;
    [SerializeField] private InputField _coordYText;

    private static GameObject _pointMarker;

    private static MapDebugHelper _instance;

    private void Awake()
    {
        _instance = this;
        _pointMarker = Resources.Load("Prefabs/PolygonMarker") as GameObject;
    }

    public void FocusOnNodeButtonCallback()
    {
        float x = float.Parse(_coordXText.text);
        float y = float.Parse(_coordYText.text);

        Camera.main.transform.position = new Vector3(x, 0.05f, y);

        GameObject pointMarker = Instantiate(_pointMarker, new Vector3(x, 0.001f, y), Quaternion.identity);
        pointMarker.transform.localScale = 0.0015f* new Vector3(1f, 1f, 1f);
    }

    public static void ConditionalNodeLog(RoadNode node, string msg)
    {
        ConditionalNodeLog(new Vector2(node.GetX(), node.GetY()), msg);
    }

    public static void ConditionalNodeLog(Vector3 point, string msg)
    {
        ConditionalNodeLog(new Vector2(point.x, point.z), msg);
    }

    public static void ConditionalNodeLog(Vector2 point, string msg)
    {
        Vector3 p = RoadMesh.TransformPointToMeshSpace(point);
        if(p.x-0.00005 < targetNodeX && p.x+0.00005 > targetNodeX
            && p.z-0.00005 < targetNodeY && p.z+0.00005 > targetNodeY)
        {
            Debug.Log(msg);
        }
    }
}
