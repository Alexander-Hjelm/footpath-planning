﻿using System.Collections;
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
    private List<RoadNode> roadNodesList;

    void Start()
    {
        roadNodeCollection = new RoadNodeCollection();

        foreach(string hwy in _highwayCategories)
        {
            FeatureCollection collection = GeoJSONImporter.ReadFeatureCollectionFromFile("MapData/" + hwy);
            foreach(FeatureObject feature in collection.features)
            {
                List<Vector2> path = new List<Vector2>();
                List<PositionObject> positions = feature.geometry.AllPositions();
                foreach(PositionObject position in positions)
                {
                    path.Add(new Vector2(position.latitude, position.longitude));
                }
                roadNodeCollection.AddPath(path);
            }
        }
        roadNodesList = roadNodeCollection.BuildToList();
    }

    void Update()
    {
        RoadNode c = roadNodesList[0];
        foreach(RoadNode a in roadNodesList)
        {
            foreach(RoadNode b in a.GetNeighbours())
            {
                Vector3 start = new Vector3((a.GetY()-18.05f)*0.5f, 0f, a.GetX()-59.34f)*20f;
                Vector3 stop = new Vector3((b.GetY()-18.05f)*0.5f, 0f, b.GetX()-59.34f)*20f;
                Debug.DrawLine(start, stop);
            }
        }
    }

}
