import shapely.geometry
import math
import numpy as np
import copy
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

def get_edges_on_rect_perimeter(polygon, rect):
    assert(len(rect)==4)
    edges_out = []
    for i in range(0, len(polygon)-1):
        for j in range(0, 3):
            point_1 = polygon[i]
            point_2 = polygon[i+1]
            corner_1 = rect[j]
            corner_2 = rect[j+1]
            if perp_distance_point_to_line(point_1, corner_1, corner_2) < 1:
                if perp_distance_point_to_line(point_2, corner_1, corner_2) < 1:
                    edges_out.append([point_1, point_2])
                continue
    return edges_out

def edge_endpoints_distance(edge_1, edge_2):
    p11 = edge_1[0]
    p12 = edge_1[1]
    p21 = edge_2[0]
    p22 = edge_2[1]
    d1 = point_distance(p11, p21) + point_distance(p12, p22)
    d2 = point_distance(p12, p21) + point_distance(p11, p22)
    return min(d1, d2)

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
    counted_points = 0
    for i in range(0, len(polygon)):
        point = polygon[i]
        if i == len(polygon)-1 and point[0] == polygon[0][0] and point[1] == polygon[0][1]:
            # Ensure that the starting point is not counted twice
            continue
        centroid[0] += point[0]
        centroid[1] += point[1]
        counted_points += 1
    centroid[0] /= counted_points
    centroid[1] /= counted_points
    return centroid

def point_distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def point_len(p):
    return point_distance(p, [0.0, 0.0])

def normalize(a):
    d = point_len(a)
    return [a[0]/d, a[1]/d]

def project(b, a):
    # Project a onto b
    proj_factor = np.dot(a, b)/(point_len(a)**2)
    return [proj_factor*a[0], proj_factor*a[1]]

def polygon_perimeter(polygon):
    perimeter_out = 0.0
    for i in range(0, len(polygon)-1):
        perimeter_out += point_distance(polygon[i], polygon[i+1])
    perimeter_out += point_distance(polygon[-1], polygon[0])
    return perimeter_out

def signed_angle(vector):
    x, y = vector
    return math.atan2(y, x)

def signed_vector_angle(vector1, vector2):
    angle_diff = signed_angle(vector2) - signed_angle(vector1)
    if angle_diff > math.pi:
        angle_diff -= 2*math.pi
    elif angle_diff < -math.pi:
        angle_diff += 2*math.pi
    return angle_diff

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

def minmax_points_of_polygon(polygon):
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

def closest_points_between_polygons(polygon_1, polygon_2):
    closest_1 = None
    closest_2 = None
    closest_index_1 = -1
    closest_index_2 = -1
    closest_d = 99999999999999.0
    for i in range(0, len(polygon_1)):
        p1 = polygon_1[i]
        for j in range(0, len(polygon_2)):
            p2 = polygon_2[j]
            d = point_distance(p1, p2)
            if d < closest_d:
                closest_1 = p1
                closest_2 = p2
                closest_index_1 = i
                closest_index_2 = j
                closest_d = d;
    return closest_1, closest_2, closest_index_1, closest_index_2

def is_polygon_clockwise(polygon):
    sum_out = 0.0
    for i in range(0, len(polygon)):
        p1 = polygon[i]
        p2 = polygon[(i+1)%len(polygon)]
        sum_out += (p2[0]-p1[0])*(p2[1]+p1[1])
    return sum_out >= 0

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

# Turning functions for two polygons
# Need to input two polygons to solve the issues of dissimilarity (clockwise/Cclockwise, starting point)
def turning_function_2(polygon_1, polygon_2):
    poly_1_rotated = copy.deepcopy(polygon_1)
    poly_2_rotated = copy.deepcopy(polygon_2)

    # Reverse the polygon enumerations if they are not clockwise
    if not is_polygon_clockwise(polygon_1):
        poly_1_rotated = poly_1_rotated[::-1]
    if not is_polygon_clockwise(polygon_2):
        poly_2_rotated = poly_2_rotated[::-1]

    # Get indices of starting points (pick the closest pair of points between the sets)
    start_point_1, start_point_2, start_index_1, start_index_2 = closest_points_between_polygons(poly_1_rotated, poly_2_rotated)

    # Rotate the polygon indices until the starting points are first in the lists
    poly_1_rotated = poly_1_rotated[start_index_1:] + poly_1_rotated[:start_index_1]
    poly_2_rotated = poly_2_rotated[start_index_2:] + poly_2_rotated[:start_index_2]

    tc_1 = turning_function(poly_1_rotated)
    tc_2 = turning_function(poly_2_rotated)

    return tc_1, tc_2

def turning_function(polygon):
    # Rotate the polygon until the starting point is first
    turnpoints_out = []
    acc_len = 0.0 # Accumluated length that has been stepped through
    total_len = polygon_perimeter(polygon)
    acc_angle = 0.0

    turnpoints_out.append([0.0, 0.0])
    for i in range(0, len(polygon)-1):
        p1 = polygon[i]
        p2 = polygon[i+1]
        p3 = polygon[(i+2)%len(polygon)]

        edge_len = point_distance(p2, p1)
        acc_len += edge_len/total_len

        turnpoints_out.append([acc_len-0.0000001, acc_angle])

        angle = signed_vector_angle([p2[0]-p1[0], p2[1]-p1[1]], [p3[0]-p2[0], p3[1]-p2[1]])
        acc_angle += angle
        turnpoints_out.append([acc_len, acc_angle])

    turnpoints_out.append([1.0, acc_angle])

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
    # (5) TODO: Try switching to the area-minimizing MBR implementation that chris sent
    cv = convex_hull(points)
    center = polygon_centroid(cv)

    best_area = 9999999999999.0
    best_corner_1 = None
    best_corner_2 = None
    best_corner_3 = None
    best_corner_4 = None

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
            p_1 = project(p, ev_1)
            p_2 = project(p, ev_2)

            if np.dot(p_1, ev_1) > np.dot(f_1_max, ev_1):
                f_1_max = p_1
            if np.dot(p_1, ev_1) < np.dot(f_1_min, ev_1):
                f_1_min = p_1
            if np.dot(p_2, ev_2) > np.dot(f_2_max, ev_2):
                f_2_max = p_2
            if np.dot(p_2, ev_2) < np.dot(f_2_min, ev_2):
                f_2_min = p_2

        c1_x = f_1_max[0] + f_2_max[0] + center[0]
        c1_y = f_1_max[1] + f_2_max[1] + center[1]
        c2_x = f_2_max[0] + f_1_min[0] + center[0]
        c2_y = f_2_max[1] + f_1_min[1] + center[1]
        c3_x = f_1_min[0] + f_2_min[0] + center[0]
        c3_y = f_1_min[1] + f_2_min[1] + center[1]
        c4_x = f_2_min[0] + f_1_max[0] + center[0]
        c4_y = f_2_min[1] + f_1_max[1] + center[1]
        corner_1 = [c1_x, c1_y]
        corner_2 = [c2_x, c2_y]
        corner_3 = [c3_x, c3_y]
        corner_4 = [c4_x, c4_y]

        area = polygon_area([corner_1, corner_2, corner_3, corner_4])
        if area < best_area:
            best_corner_1 = corner_1
            best_corner_2 = corner_2
            best_corner_3 = corner_3
            best_corner_4 = corner_4
            best_area = area

    return [best_corner_1, best_corner_2, best_corner_3, best_corner_4]

def step_functions_normalized_area_between(f1, f2):
    # Area between two normalized step functions by piecewise summation
    area_out = 0.0
    i1 = 0
    i2 = 0
    f1_normalized = []
    f2_normalized = []
    f1_start_x = f1[0][0]
    f2_start_x = f2[0][0]
    f1_total_len = f1[-1][0] - f1_start_x
    f2_total_len = f2[-1][0] - f2_start_x

    # Normalize by accumulated length
    for point in f1:
        f1_normalized.append([(point[0]-f1_start_x)/f1_total_len, point[1]])
    for point in f2:
        f2_normalized.append([(point[0]-f2_start_x)/f2_total_len, point[1]])

    while i1 < len(f1_normalized)-1 and i2 < len(f2_normalized)-1:
        p1 = f1_normalized[i1]
        p2 = f2_normalized[i2]
        p1_next = f1_normalized[i1+1]
        p2_next = f2_normalized[i2+1]

        if p1_next[0] < p2_next[0]:
            # Next evaluation point is on f1
            area_out += (p1_next[0] - p1[0]) * (p1[1]-p2[1])
            i1+=1
        elif p2_next[0] < p1_next[0]:
            # Next evaluation point is on f2
            area_out += (p2_next[0] - p2[0]) * (p1[1]-p2[1])
            i2+=1
        else:
            # p1_next.x == p2_next.x
            area_out += min(p1_next[0]-p1[0], p2_next[0]-p2[0]) * (p1[1]-p2[1])
            i1+=1
            i2+=1
    return area_out

def polygon_rectangularity(polygon):
    mbr = oriented_mbr(polygon)
    a_poly = polygon_area(polygon)
    a_rect = polygon_area(mbr)
    return a_poly/a_rect

def prune_polygon(polygon):
    points_to_remove = []
    for i in range(0, len(polygon)):
        p1 = polygon[i]
        p2 = polygon[(i+1)%len(polygon)]
        if p1[0] == p2[0] and p1[1] == p2[1]:
            points_to_remove.append(p2)
    for point in points_to_remove:
        polygon.remove(point)


def shape_dissimilarity(polygon_1, polygon_2):
    # Implementation of eqn 1, Fan et al
    tc_1, tc_2 = turning_function_2(polygon_1, polygon_2)
    area_diff = step_functions_normalized_area_between(tc_1, tc_2)
    return math.sqrt(abs(area_diff))

def normalized_shape_dissimilarity(polygon_1, polygon_2):
    # Implementation of eqn 4, Fan et al
    # Normalize shape similarity by the rectangularity of the footprints (area divided by the area of the oriented MBR)
    rectangularity = polygon_rectangularity(polygon_1)
    mbr = oriented_mbr(polygon_1)
    return 1 - shape_dissimilarity(polygon_1, polygon_2)*(1-rectangularity)/shape_dissimilarity(polygon_1, mbr)

def extract_polygon_from_feature(feature):
    feature_type = feature['geometry']['type']

    # Even for multipolygons, the big surrounding polygon is always the first one
    if feature_type == 'Polygon':
        return feature['geometry']['coordinates'][0]

    if feature_type == 'MultiPolygon':
        return feature['geometry']['coordinates'][0][0]

    print("extract_polygon_from_feature: feature type not implemented: " + feature_type)
    print(feature)
