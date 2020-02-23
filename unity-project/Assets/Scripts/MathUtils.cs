using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class MathUtils : MonoBehaviour
{
    // More here: http://wiki.unity3d.com/index.php/3d_Math_functions?_ga=2.226594461.1045422346.1582048800-1214154379.1582048800

    //create a vector of direction "vector" with length "size"
	public static Vector3 SetVectorLength(Vector3 vector, float size){
 
		//normalize the vector
		Vector3 vectorNormalized = Vector3.Normalize(vector);
 
		//scale the vector
		return vectorNormalized *= size;
	}

    //Calculate the intersection point of two lines. Returns true if lines intersect, otherwise false.
	//Note that in 3d, two lines do not intersect most of the time. So if the two lines are not in the 
	//same plane, use ClosestPointsOnTwoLines() instead.
	public static bool LineLineIntersection(out Vector3 intersection, Vector3 linePoint1, Vector3 lineVec1, Vector3 linePoint2, Vector3 lineVec2){
 
		Vector3 lineVec3 = linePoint2 - linePoint1;
		Vector3 crossVec1and2 = Vector3.Cross(lineVec1, lineVec2);
		Vector3 crossVec3and2 = Vector3.Cross(lineVec3, lineVec2);
 
		float planarFactor = Vector3.Dot(lineVec3, crossVec1and2);
 
		//is coplanar, and not parrallel
		if(Mathf.Abs(planarFactor) < 0.0001f && crossVec1and2.sqrMagnitude > 0.0001f)
		{
			float s = Vector3.Dot(crossVec3and2, crossVec1and2) / crossVec1and2.sqrMagnitude;
			intersection = linePoint1 + (lineVec1 * s);
			return true;
		}
		else
		{
			intersection = Vector3.zero;
			return false;
		}
	}

    //Get the intersection between a line and a plane. 
	//If the line and plane are not parallel, the function outputs true, otherwise false.
	public static bool LinePlaneIntersection(out Vector3 intersection, Vector3 linePoint, Vector3 lineVec, Vector3 planeNormal, Vector3 planePoint){
 
		float length;
		float dotNumerator;
		float dotDenominator;
		Vector3 vector;
		intersection = Vector3.zero;
 
		//calculate the distance between the linePoint and the line-plane intersection point
		dotNumerator = Vector3.Dot((planePoint - linePoint), planeNormal);
		dotDenominator = Vector3.Dot(lineVec, planeNormal);
 
		//line and plane are not parallel
		if(dotDenominator != 0.0f){
			length =  dotNumerator / dotDenominator;
 
			//create a vector from the linePoint to the intersection point
			vector = SetVectorLength(lineVec, length);
 
			//get the coordinates of the line-plane intersection point
			intersection = linePoint + vector;	
 
			return true;	
		}
 
		//output not valid
		else{
			return false;
		}
	}

    public static Vector3 FindCentroid(List<Vector3> points) {
        float x = 0;
        float y = 0;
        float z = 0;
        foreach (Vector3 p in points) {
            x += p.x;
            y += p.y;
            z += p.z;
        }
        Vector3 center = new Vector3(0, 0);
        center.x = x / points.Count;
        center.y = y / points.Count;
        center.z = z / points.Count;
        return center;
    }

}
