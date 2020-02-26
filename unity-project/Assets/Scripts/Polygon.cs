using UnityEngine;

public class Polygon
{
    Vector2[] _points;

    public Polygon(Vector2[] points)
    {
        _points = points;
    }

    public bool ContainsPoint(Vector2 p)
    {
        var j = _points.Length - 1;
        var inside = false;
        for (int i = 0; i < _points.Length; j = i++)
        {
            var pi = _points[i];
            var pj = _points[j];
            if (((pi.y <= p.y && p.y < pj.y) || (pj.y <= p.y && p.y < pi.y)) &&
                (p.x < (pj.x - pi.x) * (p.y - pi.y) / (pj.y - pi.y) + pi.x))
                inside = !inside;
        }
        return inside;
    }
}
