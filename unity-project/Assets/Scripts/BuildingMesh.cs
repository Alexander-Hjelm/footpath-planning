using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEditor;

public class BuildingMesh : MonoBehaviour
{
    private List<GameObject> _rendererGOs = new List<GameObject>();
    private static float _scale = 500f;
    private static float _buildingHeight = 1f;
    private static Vector2 _offset = new Vector2(-18.05f, -59.34f);

    private void OnDestroy()
    {
        foreach(GameObject go in _rendererGOs)
        {
            DestroyImmediate(go);
        }
    }

    public void GenerateMeshFromFootprints(List<BuildingFootprint> buildingFootprints)
    {
        // Start building path mesh
        List<Vector3> vertices = new List<Vector3>();
        List<Vector2> uvs = new List<Vector2>();
        List<int> triangles = new List<int>();
        List<Mesh> storedBuildingMeshes = new List<Mesh>();
        int currentMeshCounter = 0;
        int countedVertices = 0;

        foreach(BuildingFootprint buildingFootprint in buildingFootprints)
        {
            // First create the mesh we'll be working with
            if(storedBuildingMeshes.Count <= currentMeshCounter) 
            {
                storedBuildingMeshes.Add(new Mesh());
            }

            List<Vector3> footprintPoints = buildingFootprint.GetVertices();
            Vector3 centroid = MathUtils.FindCentroid(footprintPoints);
            vertices.Add(centroid);
            vertices.Add(centroid + Vector3.up*_buildingHeight);
            int centroidIndex = countedVertices;
            int centroidRaisedIndex = countedVertices+1;
            countedVertices+=2;
            for(int i=0; i<footprintPoints.Count-1; i++)
            {
                Vector3 a = footprintPoints[i];
                Vector3 b = footprintPoints[i+1];
                Vector3 a3D = RoadMesh.TransformPointToMeshSpace(a);
                Vector3 b3D = RoadMesh.TransformPointToMeshSpace(b);

                vertices.Add(a3D);
                vertices.Add(b3D);
                vertices.Add(a3D + Vector3.up*_buildingHeight);
                vertices.Add(b3D + Vector3.up*_buildingHeight);

                triangles.Add(centroidIndex);
                triangles.Add(countedVertices);
                triangles.Add(countedVertices+1);

                triangles.Add(countedVertices);
                triangles.Add(countedVertices+1);
                triangles.Add(countedVertices+2);

                triangles.Add(countedVertices+2);
                triangles.Add(countedVertices+3);
                triangles.Add(countedVertices);

                triangles.Add(centroidRaisedIndex);
                triangles.Add(countedVertices+2);
                triangles.Add(countedVertices+3);

                countedVertices += 4;

                uvs.Add(new Vector2(0f, 0f));
                uvs.Add(new Vector2(1f, 0f));
                uvs.Add(new Vector2(0f, 1f));
                uvs.Add(new Vector2(1f, 1f));

                if(vertices.Count > 20000)
                {
                    CreateNewMeshFilterWithMesh(vertices, triangles, uvs, storedBuildingMeshes[currentMeshCounter]);
                    vertices.Clear();
                    triangles.Clear();
                    uvs.Clear();
                    countedVertices = 0;
                    currentMeshCounter++;
                }
            }
        }

        // Create a last mesh to flush out any remaining vertices
        CreateNewMeshFilterWithMesh(vertices, triangles, uvs, storedBuildingMeshes[currentMeshCounter]);
        vertices.Clear();
        triangles.Clear();
        uvs.Clear();

    }

    private void CreateNewMeshFilterWithMesh(List<Vector3> vertices, List<int> triangles, List<Vector2> uvs, Mesh mesh)
    {
        GameObject go = new GameObject();
        go.transform.parent = transform;

        MeshRenderer meshRenderer = go.AddComponent(typeof(MeshRenderer)) as MeshRenderer;
        Material material = new Material(Shader.Find("Standard"));
        material.mainTexture = Resources.Load("Textures/Road") as Texture;
        meshRenderer.sharedMaterial = material;
        MeshFilter meshFilter = go.AddComponent(typeof(MeshFilter)) as MeshFilter;

        mesh.vertices = vertices.ToArray();
        mesh.triangles = triangles.ToArray();
        mesh.uv = uvs.ToArray();

        // Build normals
        Vector3[] normals = new Vector3[vertices.Count];
        for(int i=0; i<vertices.Count; i++)
        {
            normals[i] = Vector3.up;
        }
        mesh.normals = normals;

        meshFilter.mesh = mesh;

        // Store the new GameObject for later deletion
        _rendererGOs.Add(go);
    }

    public static Vector3 TransformPointToMeshSpace(Vector2 input)
    {
        return new Vector3((input.x+_offset.x)*0.5f, 0f, (input.y+_offset.y))*_scale;
    }
}
