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

# read files
with open('raw_data/buildings-osm.geojson', 'r') as f:
    OSM_data = load(f)
with open('raw_data/buildings-slu.geojson', 'r') as f:
    SLU_data = load(f)

progress = 0.0
for feature in OSM_data['features']:
    print("Converting OSM features, progess: " + str(int(100*progress/len(OSM_data['features']))) + '%')
    progress+=1.0
    for i in range(0, len(feature['geometry']['coordinates'])):
        point = feature['geometry']['coordinates'][i]
        feature['geometry']['coordinates'][i] = wgs84_to_epsg3006(point)
progress = 0.0
for feature in SLU_data['features']:
    print("Converting SLU features, progess: " + str(int(100*progress/len(SLU_data['features']))) + '%')
    progress+=1.0
    for i in range(0, len(feature['geometry']['coordinates'])):
        point = feature['geometry']['coordinates'][i]
        feature['geometry']['coordinates'][i] = wgs84_to_epsg3006(point)

# Write all building features to files
with open('raw_data/buildings-osm-sweref.geojson', 'w') as f:
    dump(FeatureCollection(OSM_data), f)
with open('raw_data/buildings-slu-sweref.geojson', 'w') as f:
    dump(FeatureCollection(SLU_data), f)
