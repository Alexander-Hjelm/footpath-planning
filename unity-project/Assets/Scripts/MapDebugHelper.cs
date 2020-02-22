using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MapDebugHelper : MonoBehaviour
{
    private static float targetNodeX = 6.144524;
    private static float targetNodeY = -7.995605;

    public static void ConditionalNodeLog(RoadNode node, string msg)
    {
        ConditionalNodeLog(new Vector2(node.GetX(), node.GetY()));
    }

    public static void ConditionalNodeLog(Vector3 point, string msg)
    {
        ConditionalNodeLog(new Vector2(point.x, point.z));
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
