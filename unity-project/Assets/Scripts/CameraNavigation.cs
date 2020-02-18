using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraNavigation : MonoBehaviour
{
    private Vector3 _moveTarget;
    [SerializeField] private float _moveSpeed = 1f;
    [SerializeField] private float _zoomSpeed = 1f;
    [SerializeField] private float _snapSpeed = 1f;
    [SerializeField] private float _minZoomLevel = 1f;
    [SerializeField] private float _maxZoomLevel = 10f;

    private void Awake()
    {
        transform.position = new Vector3(5f, 6.3f, -7.6f);
        transform.rotation = Quaternion.LookRotation(Vector3.down, Vector3.forward);
        _moveTarget = transform.position;
    }

    private void Update()
    {
        Vector3 moveOffset = Vector3.zero;

        // Movement input
        if(Input.GetKey(KeyCode.UpArrow))
        {
            moveOffset += Vector3.forward;
        }
        if(Input.GetKey(KeyCode.DownArrow))
        {
            moveOffset += Vector3.back;
        }
        if(Input.GetKey(KeyCode.RightArrow))
        {
            moveOffset += Vector3.right;
        }
        if(Input.GetKey(KeyCode.LeftArrow))
        {
            moveOffset += Vector3.left;
        }

        // Zooming input
        if(Input.GetKey(KeyCode.X))
        {
            moveOffset += Vector3.up;
        }
        if(Input.GetKey(KeyCode.Z))
        {
            moveOffset += Vector3.down;
        }

        _moveTarget += new Vector3(
            moveOffset.x*_moveSpeed,
            moveOffset.y*_zoomSpeed,
            moveOffset.z*_moveSpeed
        );

        // Zoom clamping, lower
        if(_moveTarget.y < _minZoomLevel)
        {
            _moveTarget = new Vector3(
                    _moveTarget.x,
                    _minZoomLevel,
                    _moveTarget.z
            );
        }

        // Zoom clamping, upper
        if(_moveTarget.y > _maxZoomLevel)
        {
            _moveTarget = new Vector3(
                    _moveTarget.x,
                    _maxZoomLevel,
                    _moveTarget.z
            );
        }

        transform.position = Vector3.Lerp(transform.position, _moveTarget, Time.deltaTime*_snapSpeed);
    }
}
