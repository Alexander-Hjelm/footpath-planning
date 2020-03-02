using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[RequireComponent(typeof(LineRenderer))]
public class AreaSelector : MonoBehaviour
{
    [SerializeField] private GameObject _polygonMarker;

    private LineRenderer _lineRenderer;
    private List<Vector2> _queuedPointsInPolygon = new List<Vector2>();
    private Polygon _createdPolygon = null;
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
                partialPolygonPoints[i] = new Vector3(_queuedPointsInPolygon[i].x, 0f, _queuedPointsInPolygon[i].y);
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
                Vector2 intersection2D = new Vector2(intersection.x, intersection.z);
                if(_queuedPointsInPolygon.Count > 0 && (intersection2D - _queuedPointsInPolygon[0]).magnitude < 0.2f*(zoomLevel+0.1f))
                {
                    _createdPolygon = new Polygon(_queuedPointsInPolygon.ToArray());
                    _queuedPointsInPolygon = new List<Vector2>();

                    // Call to generate a new road network inside the polygon
                    RoadGenerator.PopulatePolygonFromExamplePatches(GameManager.GetPaths(), _createdPolygon);

                    // Reset polygon markers and line renderer
                    foreach(GameObject polygonMarker in _instantiatedPolygonMakers)
                    {
                        Destroy(polygonMarker);
                    }
                    _instantiatedPolygonMakers = new List<GameObject>();
                    _lineRenderer.positionCount = 0;
                }
                else
                {
                    _queuedPointsInPolygon.Add(intersection2D);
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
