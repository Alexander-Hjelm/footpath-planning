# This script reads processed OSM and SLU building data, and finds the metrics specified in the project report
# REQUIREMENTS:
# - Run buildings-convert-to-sweref.py

from geojson import Point, Feature, FeatureCollection, load

OSM_data = {}
SLU_data = {}

def polygon_area(vertices):
    n = len(vertices) # of corners
    a = 0.0
    for i in range(n):
        j = (i + 1) % n
        a += vertices[i][0] * vertices[j][1]
        a -= vertices[j][0] * vertices[i][1]
    result = abs(a) / 2.0
    return result

def add_areas_recursively(c):
    area_out = 0.0
    if type(c) == list:
        if type(c[0][0]) == float:
            # Found a float pair
            area_out += polygon_area(c)
        else:
            for c_sub in c:
                step_recursively(c_sub)
    return area_out

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
print(total_area_OSM)
print(total_area_SLU)
