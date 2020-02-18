using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[RequireComponent(typeof(LineRenderer))]
public class AreaSelector : MonoBehaviour
{
    private LineRenderer _lineRenderer;
    private List<Vector3> _queuedPointsInPolygon = new List<Vector3>();

    private void Awake()
    {
        _lineRenderer = GetComponent<LineRenderer>();
        _lineRenderer.positionCount = 0;
    }

    private void Update()
    {
        if(_queuedPointsInPolygon.Count >= 2)
        {
            Vector3[] partialPolygonPoints = new Vector3[_queuedPointsInPolygon.Count];
            for(int i=0; i<_queuedPointsInPolygon.Count; i++)
            {
                partialPolygonPoints[i] = _queuedPointsInPolygon[i];
            }
            _lineRenderer.positionCount = partialPolygonPoints.Length;
            _lineRenderer.SetPositions(partialPolygonPoints);
        }

        if(Input.GetMouseButtonDown(0))
        {
            Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);
            Vector3 intersection;
            if(MathUtils.LinePlaneIntersection(out intersection, ray.origin, ray.direction, Vector3.up, Vector3.zero))
            {
                _queuedPointsInPolygon.Add(intersection);
            }
        }
    }
}
