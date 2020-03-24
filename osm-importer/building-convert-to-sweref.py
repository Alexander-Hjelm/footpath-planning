# Coverts processed data to sweref coordinates
# REQUIREMENTS:
# - Run building-cropper.py

from geojson import Point, Feature, FeatureCollection, load, dump
import geometry_utils

def step_recursively(c):
    if type(c) == list:
        if type(c[0]) == float and len(c) == 2:
            # Found a float pair
            c_new = geometry_utils.wgs84_to_epsg3006(c)
            c[0] = c_new[0]
            c[1] = c_new[1]
        else:
            for c_sub in c:
                step_recursively(c_sub)
    else:
        print(type(c))

# read files
with open('raw_data/buildings-osm-cropped.geojson', 'r') as f:
    OSM_data = load(f)
with open('raw_data/buildings-slu-cropped.geojson', 'r') as f:
    SLU_data = load(f)

print("Number of OSM features to convert: " + str(len(OSM_data['features'])))
print("Number of SLU features to convert: " + str(len(SLU_data['features'])))

progress = 0
for feature in OSM_data['features']:
    step_recursively(feature['geometry']['coordinates'])
    # Progress
    print("Converting OSM features, progess: " + str(progress) + "/" + str(len(OSM_data['features'])))
    progress+=1

progress = 0
for feature in SLU_data['features']:
    step_recursively(feature['geometry']['coordinates'])

    # Progress
    print("Converting SLU features, progess: " + str(progress) + "/" + str(len(SLU_data['features'])))
    progress+=1

# Write all building features to files
with open('raw_data/buildings-osm-sweref.geojson', 'w') as f:
    dump(FeatureCollection(OSM_data), f)
with open('raw_data/buildings-slu-sweref.geojson', 'w') as f:
    dump(FeatureCollection(SLU_data), f)
