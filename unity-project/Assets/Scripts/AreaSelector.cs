using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[RequireComponent(typeof(LineRenderer))]
public class AreaSelector : MonoBehaviour
{
    [SerializeField] private GameObject _polygonMarker;

    private LineRenderer _lineRenderer;
    private List<Vector3> _queuedPointsInPolygon = new List<Vector3>();
    private List<Vector3> _createdPolygon = new List<Vector3>();
    private List<GameObject> _instantiatedPolygonMakers = new List<GameObject>();

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

        // Line width and marker size dependent on zoom level
        float zoomLevel = CameraNavigation.GetZoomLevel();
        _lineRenderer.startWidth = (zoomLevel+0.1f)*0.1f;
        _lineRenderer.endWidth = (zoomLevel+0.1f)*0.1f;
        for(int i=0; i<_instantiatedPolygonMakers.Count; i++)
        {
            _instantiatedPolygonMakers[i].transform.localScale = new Vector3(1f, 1f, 1f)*(zoomLevel+0.1f)*0.5f;
        }

        if(Input.GetMouseButtonDown(0))
        {
            Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);
            Vector3 intersection;
            if(MathUtils.LinePlaneIntersection(out intersection, ray.origin, ray.direction, Vector3.up, Vector3.zero))
            {
                // If the click was nearby the first marker, create the polygon
                if(_queuedPointsInPolygon.Count > 0 && (intersection - _queuedPointsInPolygon[0]).magnitude < 0.2f*(zoomLevel+0.1f))
                {
                    _createdPolygon = _queuedPointsInPolygon;
                    _queuedPointsInPolygon = new List<Vector3>();
                    foreach(GameObject polygonMarker in _instantiatedPolygonMakers)
                    {
                        Destroy(polygonMarker);
                    }
                    _instantiatedPolygonMakers = new List<GameObject>();
                    _lineRenderer.positionCount = 0;
                }
                else
                {
                    _queuedPointsInPolygon.Add(intersection);
                    GameObject polygonMarker = Instantiate(_polygonMarker, intersection, Quaternion.identity);
                    _instantiatedPolygonMakers.Add(polygonMarker);
                }
            }
        }

        // Backspace is undo
        if(Input.GetKeyDown(KeyCode.Backspace) && _queuedPointsInPolygon.Count > 0)
        {
            _queuedPointsInPolygon.RemoveAt(_queuedPointsInPolygon.Count-1);
            Destroy(_instantiatedPolygonMakers[_instantiatedPolygonMakers.Count-1]);
            _instantiatedPolygonMakers.RemoveAt(_instantiatedPolygonMakers.Count-1);
            _lineRenderer.positionCount = Mathf.Max(0,_lineRenderer.positionCount-1);
        }
    }
}
