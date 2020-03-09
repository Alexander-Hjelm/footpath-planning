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

    public Vector2 GetCenter()
    {
        Vector2 centroid = new Vector2(0f, 0f);
        float signedArea = 0f;
        float x0 = 0f; // Current vertex X
        float y0 = 0f; // Current vertex Y
        float x1 = 0f; // Next vertex X
        float y1 = 0f; // Next vertex Y
        float a = 0f;  // Partial signed area

        // For all vertices except last
        int i=0;
        for (i=0; i<_points.Length-1; ++i)
        {
            x0 = _points[i].x;
            y0 = _points[i].y;
            x1 = _points[i+1].x;
            y1 = _points[i+1].y;
            a = x0*y1 - x1*y0;
            signedArea += a;
            centroid.x += (x0 + x1)*a;
            centroid.y += (y0 + y1)*a;
        }

        // Do last vertex separately to avoid performing an expensive
        // modulus operation in each iteration.
        x0 = _points[i].x;
        y0 = _points[i].y;
        x1 = _points[0].x;
        y1 = _points[0].y;
        a = x0*y1 - x1*y0;
        signedArea += a;
        centroid.x += (x0 + x1)*a;
        centroid.y += (y0 + y1)*a;

        signedArea *= 0.5f;
        centroid.x /= (6.0f*signedArea);
        centroid.y /= (6.0f*signedArea);

        return centroid;

    }

    public string ToString()
    {
        string outStr = "";
        for(int i=0; i<_points.Length; i++)
        {
            outStr += _points[i];
            if(i<_points.Length-1)
                outStr += ", ";
        }
        return outStr;
    }
}
