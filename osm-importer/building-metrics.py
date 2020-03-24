# This script reads processed OSM and SLU building data, and finds the metrics specified in the project report
# REQUIREMENTS:
# - Run buildings-convert-to-sweref.py

from geojson import Point, Feature, FeatureCollection, load
import shapely.geometry
import math

OSM_data = {}
SLU_data = {}

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

def minmax_points_of_polygon_with_offset(polygon):
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

# read files
with open('raw_data/buildings-osm-sweref.geojson', 'r') as f:
    OSM_data = load(f)
with open('raw_data/buildings-slu-sweref.geojson', 'r') as f:
    SLU_data = load(f)

print("Finished loading map data")

# Metric: total building area
total_area_OSM = 0.0
total_area_SLU = 0.0
for feature in OSM_data['features']:
    total_area_OSM += add_areas_recursively(feature['geometry']['coordinates'])
for feature in SLU_data['features']:
    total_area_SLU += add_areas_recursively(feature['geometry']['coordinates'])
print("Total area, OSM: " + str(total_area_OSM))
print("Total area, SLU: " + str(total_area_SLU))
print("Total area, fraction: " + str(total_area_OSM / total_area_SLU))

# Feature mapping
overlapping_buildings_osm_bigger = {}
overlapping_buildings_slu_bigger = {}
progress = 0.0
for feature_osm in OSM_data['features']:
    # Debug only, limit the wating time
    if progress>10:
        break
    print("Mapping features, progess: " + str(int(100*progress/len(OSM_data['features']))) + '%')
    progress+=1.0

    # Build polygon and match with SLU polygons
    polygon_osm = extract_polygon_from_feature(feature_osm)
    for feature_slu in SLU_data['features']:
        polygon_slu = extract_polygon_from_feature(feature_slu)

        relative_overlap = polygon_relative_overlap(polygon_osm, polygon_slu)
        if relative_overlap > 0.3:
            if polygon_area(polygon_slu) > polygon_area(polygon_osm):
                if not feature_slu['id'] in overlapping_buildings_slu_bigger.keys:
                    overlapping_buildings_slu_bigger[feature_slu['id']] = []
                overlapping_buildings_slu_bigger[feature_slu['id']].append(feature_osm)
            else:
                if not feature_osm['id'] in overlapping_buildings_osm_bigger.keys:
                    overlapping_buildings_osm_bigger[feature_osm['id']] = []
                overlapping_buildings_osm_bigger[feature_osm['id']].append(feature_slu)

#TODO: Bounding polygon method
