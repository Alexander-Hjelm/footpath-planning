# This script reads processed OSM and SLU building data, and finds the metrics specified in the project report
# REQUIREMENTS:
# - Run buildings-convert-to-sweref.py

from geojson import Point, Feature, FeatureCollection, load
import geometry_utils

OSM_data = {}
SLU_data = {}

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
    total_area_OSM += geometry_utils.add_areas_recursively(feature['geometry']['coordinates'])
for feature in SLU_data['features']:
    total_area_SLU += geometry_utils.add_areas_recursively(feature['geometry']['coordinates'])
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
    polygon_osm = geometry_utils.extract_polygon_from_feature(feature_osm)
    for feature_slu in SLU_data['features']:
        polygon_slu = geometry_utils.extract_polygon_from_feature(feature_slu)

        relative_overlap = geometry_utils.polygon_relative_overlap(polygon_osm, polygon_slu)
        if relative_overlap > 0.3:
            if geometry_utils.polygon_area(polygon_slu) > geometry_utils.polygon_area(polygon_osm):
                if not feature_slu['id'] in overlapping_buildings_slu_bigger.keys():
                    overlapping_buildings_slu_bigger[feature_slu['id']] = []
                overlapping_buildings_slu_bigger[feature_slu['id']].append(feature_osm)
            else:
                if not feature_osm['id'] in overlapping_buildings_osm_bigger.keys():
                    overlapping_buildings_osm_bigger[feature_osm['id']] = []
                overlapping_buildings_osm_bigger[feature_osm['id']].append(feature_slu)

# Calculate turning functions
for feature_osm in OSM_data['features']:
    #TODO: Turning function on the convex hull for now? Otherwise no way to map the multiple SLU
    # Footprints to a single OSM footprint
    if feature_osm['id'] in overlapping_buildings_osm_bigger:
        features_slu = overlapping_buildings_osm_bigger[feature_osm['id']]

        # Build polygons
        polygon_osm = geometry_utils.extract_polygon_from_feature(feature_osm)
        polygon_slu = []
        for feature_slu in features_slu:
            polygon_slu += geometry_utils.extract_polygon_from_feature(feature_slu)

        # Turning funcitons
        tc_osm = geometry_utils.turning_function(polygon_osm)
        #tc_slu = geometry_utils.turning_function(polygon_slu)

#TODO: Calculate Douglas-Peucker-reduced polygons
#TODO: Bounding points of Douglas-Peucker-reduced polygons
#TODO: Include point indices with Douglas-Peucker reduction
#TODO: Map to the original points before the reduction
#TODO: Point distance
#TODO: Point distance average



