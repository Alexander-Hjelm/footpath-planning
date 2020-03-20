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
with open('raw_data/buildings-osm.geojson', 'r') as f:
    OSM_data = load(f)
with open('raw_data/buildings-slu.geojson', 'r') as f:
    SLU_data = load(f)

OSM_data_out = []
SLU_data_out = []

for feature in SLU_data['features']:
    SLU_data_out.append(feature)

query_polygon = [[q_bbox_w, q_bbox_n],[q_bbox_e, q_bbox_n],[q_bbox_e, q_bbox_s],[q_bbox_w, q_bbox_s],[q_bbox_w, q_bbox_n]]

# Delete any SLU buildings that are outside of the new projected query box
for feature in SLU_data_out:
    polygon = extract_polygon_from_feature(feature)
    if polygon_intersection_area(polygon, query_polygon) == 0.0:
        SLU_data_out.remove(feature)
        print('Remaining SLU features: ' + str(len(SLU_data_out)))

progress = 0.0
for feature_osm in OSM_data['features']:
    print("Cropping OSM features, progess: " + str(int(100*progress/len(OSM_data['features']))) + '%')
    progress+=1.0

    # Build polygon
    polygon_osm = extract_polygon_from_feature(feature_osm)
    if polygon_intersects_query_bbox(polygon_osm):
        for feature_slu in SLU_data_out:
            polygon_slu = extract_polygon_from_feature(feature_slu)

            relative_overlap = polygon_relative_overlap(polygon_osm, polygon_slu)
            if relative_overlap > 0.3:
                SLU_data_out.remove(feature_slu)
                print('Remaining SLU features: ' + str(len(SLU_data_out)))

    else:
        OSM_data_out.append(feature_osm)

# Write all building features to files
with open('raw_data/buildings-osm-cropped.geojson', 'w') as f:
    dump(FeatureCollection(OSM_data_out), f)
with open('raw_data/buildings-slu-cropped.geojson', 'w') as f:
    dump(FeatureCollection(SLU_data_out), f)
