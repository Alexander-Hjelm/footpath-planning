using System.Collections.Generic;
using UnityEngine;

public class RoadNode
{
    public enum HighwayType
    {
        FOOTPATH,
        RESIDENTIAL,
        SECONDARY,
        PRIMARY,
        NONE
    }

    private static Dictionary<string, HighwayType> validHwyTypeStrings = new Dictionary<string, HighwayType>()
    {
        {"footpath", HighwayType.FOOTPATH},
        {"Footpath", HighwayType.FOOTPATH},
        {"FootPath", HighwayType.FOOTPATH},
        {"FOOTPATH", HighwayType.FOOTPATH},
        {"residential", HighwayType.RESIDENTIAL},
        {"Residential", HighwayType.RESIDENTIAL},
        {"RESIDENTIAL", HighwayType.RESIDENTIAL},
        {"secondary", HighwayType.SECONDARY},
        {"Secondary", HighwayType.SECONDARY},
        {"SECONDARY", HighwayType.SECONDARY},
        {"primary", HighwayType.PRIMARY},
        {"Primary", HighwayType.PRIMARY},
        {"PRIMARY", HighwayType.PRIMARY}
    };

    private float _xCoord;
    private float _yCoord;
    private HighwayType _highwayType;
    private string _pathId;
    private bool _intersection;

    public static HighwayType GetHighwayTypeFromString(string input)
    {
        return validHwyTypeStrings[input];
    }


    public RoadNode(float x, float y, HighwayType highwayType, string pathId)
    {
        _xCoord = x;
        _yCoord = y;
        _highwayType = highwayType;
        _pathId = pathId;
        _intersection = false;
    }

    public RoadNode(Vector2 pos, HighwayType highwayType):
        this(pos.x, pos.y, highwayType, "")
    {
    }

    public float GetX()
    {
        return _xCoord;
    }

    public float GetY()
    {
        return _yCoord;
    }

    public HighwayType GetHighwayType()
    {
        return _highwayType;
    }

    public Vector2 GetPosAsVector2()
    {
        return new Vector2(_xCoord, _yCoord);
    }

    public bool IsIntersection()
    {
        return _intersection;
    }

    public void SetIntersection()
    {
        _intersection = true;
    }

}
