using System.Collections.Generic;
using UnityEngine;

public class RoadNode
{
    private float _xCoord;
    private float _yCoord;

    public RoadNode(float x, float y)
    {
        _xCoord = x;
        _yCoord = y;
    }

    public float GetX()
    {
        return _xCoord;
    }

    public float GetY()
    {
        return _yCoord;
    }

    public Vector2 GetPosAsVector2()
    {
        return new Vector2(_xCoord, _yCoord);
    }

}
