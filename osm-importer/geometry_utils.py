import shapely.geometry
import math
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

def point_distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

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
    min_point_n = []
    min_point_e = []
    min_point_s = []
    min_point_w = []

    for point in polygon:
        if point.y > min_point_n:
            min_point_n = point
        if point.x > min_point_e:
            min_point_e = point
        if point.y < min_point_s:
            min_point_s = point
        if point.x < min_point_w:
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
    # Find starting points, use northernmost point and the furthest point from that
    #Pick northernmost point to ensure it is the same in both OSM and SLU cases
    sp_1 = None
    xy_max = 0.0
    for i in range(0, len(polygon)):
        p = polygon[i]
        x = p[0]
        y = p[1]
        if x+y < xy_max:
            xy_max = x+y
            sp_1 = p

    sp_2 = None
    r_max = 0.0
    for i in range(0, len(polygon)):
        p = polygon[i]
        r = point_distance(sp_1, p)
        if r > r_max:
            r_max = r
            sp_2 = p

    sp_1_index = polygon.index(sp_1)
    sp_2_index = polygon.index(sp_2)
    if sp_1_index < sp_2_index:
        temp = sp_1_index
        sp_1_index = sp_2_index
        sp_2_index = temp

    slice_1 = polygon[:sp_1_index] + polgon[sp_2_index:]
    slice_2 = polgon[sp_1_index:sp_2_index]

    res_polygon_1 = douglas_peucker_helper(slice_1)
    res_polygon_2 = douglas_peucker_helper(slice_2)

    return res_polygon_1 + res_polygon_2

def douglas_peucker_helper(polygon, e):
    # TODO: geodata polygons have the first and last elements the same. Does this implementation support that?
    # Find the point with the maximum distance to the line: polygon[0], polygon[end]
    d_max = 0
    index = 0
    end = len(polygon)
    for i in range(1, end-1):
        d = perp_distance_point_to_line(polygon[i], polygon[0], polygon[end])
        if d > d_max:
            index = i
            d_max = d

    polygon_out = []
    #If max distance is greater than epsilon, recursively simplify
    if d_max > e:
        # Recursive call
        rec_polygon_1 = douglas_peucker(polygon[:index], e)
        rec_polygon_2 = douglas_peucker(polygon[index:], e)
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
