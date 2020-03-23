# Coverts processed data to sweref coordinates
# REQUIREMENTS:
# - Run building-cropper.py

from geojson import Point, Feature, FeatureCollection, load, dump
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

def step_recursively(c):
    if type(c) == list:
        if type(c[0]) == float and len(c) == 2:
            # Found a float pair
            c_new = wgs84_to_epsg3006(c)
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

progress = 0.0
for feature in OSM_data['features']:
    step_recursively(feature['geometry']['coordinates'])
    # Progress
    print("Converting OSM features, progess: " + str(int(100*progress/len(OSM_data['features']))) + '%')
    progress+=1.0

progress = 0.0
for feature in SLU_data['features']:
    step_recursively(feature['geometry']['coordinates'])

    # Progress
    print("Converting SLU features, progess: " + str(int(100*progress/len(SLU_data['features']))) + '%')

# Write all building features to files
with open('raw_data/buildings-osm-sweref.geojson', 'w') as f:
    dump(FeatureCollection(OSM_data), f)
with open('raw_data/buildings-slu-sweref.geojson', 'w') as f:
    dump(FeatureCollection(SLU_data), f)
