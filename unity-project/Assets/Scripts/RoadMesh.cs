using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RoadMesh : MonoBehaviour
{
    private MeshRenderer _meshRenderer;

    public void Awake()
    {
        _meshRenderer = gameObject.AddComponent(typeof(MeshRenderer)) as MeshRenderer;
    }

    public void GenerateMeshFromPoints(List<Vector2> points)
    {

    }
}
