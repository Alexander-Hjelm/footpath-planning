import shapely.geometry
import math
import numpy as np
from pyproj import Proj, transform

def wgs84_to_epsg3006(point):
    x = point[0]
    y = point[1]
    # Coordinate conversion from EPSG:3006 to WGS:84
    # Transform using pyproj
    WGS84 = Proj('EPSG:4326')
    SWEREF = Proj('EPSG:3006')
    # Perform the transformation. SLU data has flipped x/y coordinates
    x_new, y_new = transform(WGS84, SWEREF, y, x)
    return (y_new, x_new)

def epsg3006_to_wgs84(point):
    x = point[0]
    y = point[1]
    # Coordinate conversion from EPSG:3006 to WGS:84
    # Transform using pyproj
    WGS84 = Proj('EPSG:4326')
    SWEREF = Proj('EPSG:3006',preserve_units=False)
    # Perform the transformation. SLU data has flipped x/y coordinates
    x_new, y_new = transform(SWEREF, WGS84, y, x)
    return (y_new, x_new)

def polygon_intersection_area(polygon_1, polygon_2):
    shapely_poly_1 = shapely.geometry.Polygon(polygon_1)
    shapely_poly_2 = shapely.geometry.Polygon(polygon_2)
    return shapely_poly_1.intersection(shapely_poly_2).area

def polygon_area(polygon):
    shapely_poly = shapely.geometry.Polygon(polygon)
    return shapely_poly.area

def polygon_relative_overlap(polygon_1, polygon_2):
    area_overlap = polygon_intersection_area(polygon_1, polygon_2)
    area_1 = polygon_area(polygon_1)
    area_2 = polygon_area(polygon_2)
    return area_overlap / min(area_1, area_2)

def polygon_line_intersection(polygon, line_point_1, line_point_2):
    shapely_poly = shapely.geometry.Polygon(polygon)
    shapely_line = shapely.geometry.LineString([line_point_1, line_point_2])
    intersection_line = shapely_poly.intersection(shapely_line)

    if intersection_line.length == 0.0:
        return False
    return True

def polygon_centroid(polygon):
    centroid = [0.0, 0.0]
    for i in range(0, len(polygon)):
        point = polygon[i]
        if i == len(polygon)-1 and point[0] == polygon[0][0] and point[1] == polygon[0][1]:
            # Ensure that the starting point is not counted twice
            continue
        centroid[0] += point[0]
        centroid[1] += point[1]
    centroid[0] /= len(polygon)
    centroid[1] /= len(polygon)
    return centroid

def point_distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def point_len(p):
    return point_distance(p, [0.0, 0.0])

def normalize(a):
    d = point_len(a)
    return [a[0]/d, a[1]/d]

def project(a, b):
    # Project a onto b
    proj_factor = np.dot(a, b)/point_len(a)**2
    return [proj_factor*a[0], proj_factor*a[1]]

def polygon_perimeter(polygon):
    perimeter_out = 0.0
    for i in range(0, len(polygon)-1):
        perimeter_out += point_distance(polygon[i], polygon[i+1])
    return perimeter_out

def signed_vector_angle(vector1, vector2):
    x1, y1 = vector1
    x2, y2 = vector2
    inner_product = x1*x2 + y1*y2
    len1 = math.hypot(x1, y1)
    len2 = math.hypot(x2, y2)
    return math.acos(inner_product/(len1*len2))

def perpendicular(a):
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b

def add_areas_recursively(c):
    area_out = 0.0
    if type(c) == list:
        if type(c[0][0]) == list and type(c[0][0][0] == float):
            # Found a multipolygon. Add the area of the first (bounding) polygon,
            # and subtract the rest (holes)
            area_out += polygon_area(c[0])
            for i in range(1, len(c)):
                area_out -= polygon_area(c[i])
        elif type(c[0][0]) == float:
            # Found a list of coordinates, bottom level
            if len(c) == 0:
                area_out += polygon_area(c)
        else:
            for c_sub in c:
                area_out += add_areas_recursively(c_sub)
    return area_out

def minimum_bounding_rectangle(polygon):
    pass

def minmax_points_of_polygon(polygon):
    # TODO: Using this instead of MBR for now, since I have not figured out how to do rotated MBR
    min_point_n = [0.0, -999999999.0]
    min_point_e = [-999999999.0, 0.0]
    min_point_s = [0.0, 999999999.0]
    min_point_w = [999999999.0, 0.0]

    for point in polygon:
        if point[1] > min_point_n[1]:
            min_point_n = point
        if point[0] > min_point_e[0]:
            min_point_e = point
        if point[1] < min_point_s[1]:
            min_point_s = point
        if point[0] < min_point_w[0]:
            min_point_w = point

    return [min_point_n, min_point_e, min_point_s, min_point_w]

def perp_distance_point_to_line(point, line_point_1, line_point_2):
    x0 = point[0]
    y0 = point[1]
    x1 = line_point_1[0]
    y1 = line_point_1[1]
    x2 = line_point_2[0]
    y2 = line_point_2[1]
    nom = abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1)
    denom = math.sqrt((y2-y1)**2 + (x2-x1)**2)
    return nom/denom
def douglas_peucker(polygon, e):
    # Find starting point, use northernmost point
    #Pick northernmost point to ensure it is the same in both OSM and SLU cases
    sp_index = 0
    y_max = 999999999999.0
    for i in range(0, len(polygon)):
        p = polygon[i]
        if p[1] < y_max:
            y_max = p[1]
            sp_index = i

    # Rotate the polygon until the starting point is first
    polygon_rotated = polygon[sp_index:] + polygon[:sp_index]

    return douglas_peucker_helper(polygon_rotated, e)

def douglas_peucker_helper(polygon, e):
    # Find the point with the maximum distance to the line: polygon[0], polygon[end]
    d_max = 0
    index = 0
    end = len(polygon)-1
    for i in range(1, end):
        d = perp_distance_point_to_line(polygon[i], polygon[0], polygon[end])
        if d > d_max:
            index = i
            d_max = d

    polygon_out = []
    #If max distance is greater than epsilon, recursively simplify
    if d_max > e:
        # Recursive call
        rec_polygon_1 = douglas_peucker_helper(polygon[:index], e)
        rec_polygon_2 = douglas_peucker_helper(polygon[index:], e)
        # Build the result list
        polygon_out = rec_polygon_1 + rec_polygon_2
    else:
        polygon_out = [polygon[0], polygon[end]]
    return polygon_out

def turning_function(polygon):
    turnpoints_out = []
    acc_len = 0.0 # Accumluated length that has been stepped through
    total_len = polygon_perimeter(polygon)
    acc_angle = 0.0
    for i in range(0, len(polygon)-2):
        p1 = polygon[i]
        p2 = polygon[i+1]
        p3 = polygon[i+2]

        edge_len = point_distance(p2, p1)
        acc_len += edge_len

        angle = signed_vector_angle([p2[0]-p1[0], p2[1]-p1[1]], [p3[0]-p2[0], p3[1]-p2[1]])
        acc_angle += angle
        turnpoints_out.append([acc_len, acc_angle])
    return turnpoints_out

def get_vector_orientation(origin, p1, p2):
        '''
        Returns the orientation of the Point p1 with regards to Point p2 using origin.
        Negative if p1 is clockwise of p2.
        :param p1:
        :param p2:
        :return: integer
        '''
        difference = (p2[0] - origin[0]) * (p1[1] - origin[1]) - (p1[0] - origin[0]) * (p2[1] - origin[1])
        return difference


def convex_hull(polygons):
    hull_points = []

    # Build master polygon
    if type(polygons[0][0]) == list:
        points = []
        for p in polygons:
            points += p
    elif type(polygons[0][0]) == float:
        points = polygons

    start = points[0]
    min_x = start[0]
    for p in points[1:]:
        if p[0] < min_x:
            min_x = p[0]
            start = p

    point = start
    hull_points.append(start)

    far_point = None
    while far_point is not start:
        # get the first point (initial max) to use to compare with others
        p1 = None
        for p in points:
            if p is point:
                continue
            else:
                p1 = p
                break

        far_point = p1

        for p2 in points:
            # ensure we aren't comparing to self or pivot point
            if p2 is point or p2 is p1:
                continue
            else:
                direction = get_vector_orientation(point, far_point, p2)
                if direction > 0:
                    far_point = p2

        hull_points.append(far_point)
        point = far_point
    return hull_points

def oriented_mbr(points):
    cv = convex_hull(points)
    center = polygon_centroid(cv)

    best_area = 0.0
    best_f_1_min = None
    best_f_1_max = None
    best_f_2_min = None
    best_f_2_max = None

    for i in range(0, len(cv)-1):
        a = cv[i]
        b = cv[i+1]
        ev_1 = [b[0]-a[0], b[1]-a[1]]
        ev_1 = normalize(ev_1)
        ev_2 = perpendicular(ev_1)

        # Projected edge points from the center
        f_1_min = [0.0, 0.0]
        f_1_max = [0.0, 0.0]
        f_2_min = [0.0, 0.0]
        f_2_max = [0.0, 0.0]

        for j in range(0, len(cv)-1):
            # p = cv[j] - center
            p = [cv[j][0] - center[0], cv[j][1] - center[1]]
            print("%%%")
            print(cv[j])
            print(center)
            print(p)
            print("%%%")

            p_1 = project(p, ev_1)
            p_2 = project(p, ev_2)

            print("***")
            print(np.dot(p_1, ev_1))
            print(np.dot(f_1_max, ev_1))
            print("***")

            if np.dot(p_1, ev_1) > np.dot(f_1_max, ev_1):
                f_1_max = p_1
            if np.dot(p_1, ev_1) < np.dot(f_1_min, ev_1):
                f_1_min = p_1
            if np.dot(p_2, ev_2) > np.dot(f_2_max, ev_2):
                f_2_max = p_2
            if np.dot(p_2, ev_2) > np.dot(f_2_min, ev_2):
                f_2_min = p_2

        print(f_1_max)
        print(f_1_min)
        print(f_2_max)
        print(f_2_min)

        area = polygon_area([f_1_min, f_2_min, f_1_max, f_2_max])
        print(area)
        if area > best_area:
            best_f_1_min = f_1_min
            best_f_1_max = f_1_max
            best_f_2_min = f_2_min
            best_f_2_max = f_2_max

    c1_x = best_f_1_max[0] + best_f_2_max[0] + center[0]
    c1_y = best_f_1_max[1] + best_f_2_max[1] + center[1]
    c2_x = best_f_2_max[0] + best_f_2_min[0] + center[0]
    c2_y = best_f_2_max[1] + best_f_2_min[1] + center[1]
    c3_x = best_f_2_min[0] + best_f_1_min[0] + center[0]
    c3_y = best_f_2_min[1] + best_f_1_min[1] + center[1]
    c4_x = best_f_1_min[0] + best_f_1_max[0] + center[0]
    c4_y = best_f_1_min[1] + best_f_1_max[1] + center[1]
    corner_1 = [c1_x, c1_y]
    corner_2 = [c2_x, c2_y]
    corner_3 = [c3_x, c3_y]
    corner_4 = [c4_x, c4_y]

    return [corner_1, corner_2, corner_3, corner_4]

def extract_polygon_from_feature(feature):
    feature_type = feature['geometry']['type']

    if feature_type == 'Polygon':
        # Even for multipolygons, the big surrounding polygon is always the first one
        return feature['geometry']['coordinates'][0]

    if feature_type == 'MultiPolygon':
        #TODO: Return the very first polygon for now. Is this correct?
        return feature['geometry']['coordinates'][0][0]

    print("extract_polygon_from_feature: feature type not implemented: " + feature_type)
    print(feature)
