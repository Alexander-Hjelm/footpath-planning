# This script reads processed OSM and SLU building data, and finds the metrics specified in the project report
# REQUIREMENTS:
# - Run convert-to-sweref.py

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

# read files
with open('raw_data/osm_buildings_sweref.geojson', 'r') as f:
    OSM_data = load(f)
with open('raw_data/slu_buildings_sweref.geojson', 'r') as f:
    SLU_data = load(f)

print("Finished loading map data")

# Metric: total building area
total_area_OSM = 0.0
total_area_SLU = 0.0
for feature in OSM_data['features']:
    total_area_OSM += polygon_area(feature['geometry']['coordinates'])
for feature in SLU_data['features']:
    total_area_SLU += polygon_area(feature['geometry']['coordinates'])
print(total_area_OSM)
print(total_area_SLU)
