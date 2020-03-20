# Processes data with good vertex structure. Removes OSM buildings that interect the edge
# of an OSM query, and the corresponding overlapping buildings in the SLU set
# REQUIREMENTS:
# - Run building-data-formatter-osm.py
# - Run building-data-formatter-slu.py

from geojson import Point, Feature, FeatureCollection, load, dump
from pyproj import Proj, transform
import shapely.geometry

q_bbox_n = 59.34469860821763
q_bbox_e = 18.066052311607727
q_bbox_s = 59.328128796834925
q_bbox_w = 18.03809503228281

def polygon_line_intersection(polygon, line_point_1, line_point_2):
    shapely_poly = shapely.geometry.Polygon(polygon)
    shapely_line = shapely.geometry.LineString([line_point_1, line_point_2])
    intersection_line = shapely_poly.intersection(shapely_line)

    if intersection_line.length == 0.0:
        return False
    return True

def polygon_intersects_query_bbox(polygon):
    if polygon_line_intersection(polygon, (q_bbox_w, q_bbox_n), (q_bbox_e, q_bbox_n)):
        return True
    if polygon_line_intersection(polygon, (q_bbox_e, q_bbox_n), (q_bbox_e, q_bbox_s)):
        return True
    if polygon_line_intersection(polygon, (q_bbox_e, q_bbox_s), (q_bbox_w, q_bbox_s)):
        return True
    if polygon_line_intersection(polygon, (q_bbox_w, q_bbox_s), (q_bbox_w, q_bbox_n)):
        return True
    return False

def polygon_relative_overlap(polygon_1, polygon_2):
    return 0.0

def extract_polygon_from_feature(feature):
    feature_type = feature['geometry']['type']

    if feature_type == 'Polygon':
        # Even for multipolygons, the big surrounding polygon is always the first one
        return feature_osm['geometry']['coordinates'][0]

    print("extract_polygon_from_feature: feature type not implemented: " + feature)

# read files
with open('raw_data/buildings-osm.geojson', 'r') as f:
    OSM_data = load(f)
with open('raw_data/buildings-slu.geojson', 'r') as f:
    SLU_data = load(f)

progress = 0.0
for feature_osm in OSM_data['features']:
    print("Cropping, progess: " + str(int(100*progress/len(OSM_data['features']))) + '%')
    progress+=1.0

    # Build polygon
    polygon_osm = extract_polygon_from_feature(feature_osm)
    if polygon_intersects_query_bbox(polygon_osm):

        for feature_slu in SLU_data['features']:
            polygon_slu = feature_slu['geometry']['coordinates']

            if polygon_relative_overlap(polygon_osm, polygon_slu) > 0.3:
                SLU_data['features'].remove(feature_slu)

        OSM_data['features'].remove(feature_osm)

# Write all building features to files
with open('raw_data/buildings-osm.geojson', 'w') as f:
    dump(FeatureCollection(OSM_data), f)
with open('raw_data/buildings-slu.geojson', 'w') as f:
    dump(FeatureCollection(SLU_data), f)
