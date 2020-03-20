# Processes data with good vertex structure. Removes OSM buildings that interect the edge
# of an OSM query, and the corresponding overlapping buildings in the SLU set
# REQUIREMENTS:
# - Run building-vertex-formatter.py

from geojson import Point, Feature, FeatureCollection, load, dump
from pyproj import Proj, transform

query_bbox_n = 59.34469860821763
query_bbox_e = 18.066052311607727
query_bbox_s = 59.328128796834925
query_bbox_w = 18.03809503228281

def polygon_line_intersection(polygon, line_point, line_vec):
    return False

def polygon_intersects_query_bbox(polygon):
    if polygon_line_intersection(polygon, (query_bbox_w, query_bbox_n), (0.0, 1.0)):
        return True
    if polygon_line_intersection(polygon, (query_bbox_w, query_bbox_n), (1.0, 0.0)):
        return True
    if polygon_line_intersection(polygon, (query_bbox_e, query_bbox_s), (0.0, 1.0)):
        return True
    if polygon_line_intersection(polygon, (query_bbox_e, query_bbox_s), (1.0, 0.0)):
        return True
    return False

def polygon_relative_overlap(polygon_1, polygon_2):
    return 0.0

# read files
with open('raw_data/buildings-osm.geojson', 'r') as f:
    OSM_data = load(f)
with open('raw_data/buildings-slu.geojson', 'r') as f:
    SLU_data = load(f)

progress = 0.0
for feature_osm in OSM_data['features']:
    print("Cropping, progess: " + str(int(100*progress/len(OSM_data['features']))) + '%')
    progress+=1.0

    polygon_osm = feature_osm['geometry']['coordinates']
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
