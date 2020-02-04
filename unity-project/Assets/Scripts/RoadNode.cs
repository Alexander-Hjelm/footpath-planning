using System.Collections.Generic;

public class RoadNode
{
    private float _xCoord;
    private float _yCoord;

    private List<RoadNode> _neighbours = new List<RoadNode>();

    public RoadNode(float x, float y)
    {
        _xCoord = x;
        _yCoord = y;
    }

    public void AddNeighbour(RoadNode other)
    {
        _neighbours.Add(other);
    }

    public float GetX()
    {
        return _xCoord;
    }

    public float GetY()
    {
        return _yCoord;
    }

    public List<RoadNode> GetNeighbours()
    {
        return _neighbours;
    }

}
