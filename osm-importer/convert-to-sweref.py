# Coverts processed data to a simple geometric structure in sweref coordinates
# REQUIREMENTS:
# - Run building-data-formatter.py
# - Run plot-shp-reader.py

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

def get_vertices_of_feature(feature):
    coordinates = feature['geometry']['coordinates']
    vertices_out = []
    for point in coordinates:
        if type(point) == tuple:
            vertices_out.append(coordinates[point])
        elif type(point) == list:
            for k in range(0, len(point)):
                if type(point) == tuple:
                    vertices_out.append(point[k])
                elif type(point[k]) == list:
                    if len(point[k]) == 2:
                        vertices_out.append((point[k][0], point[k][1]))
                    else:
                        if type(point[k]) == list:
                            for l in range(0, len(point[k])):
                                vertices_out.append((point[k][l][0], point[k][l][1]))

    return vertices_out

# read files
with open('raw_data/buildings.geojson', 'r') as f:
    OSM_data = load(f)
with open('raw_data/plots.geojson', 'r') as f:
    SLU_data = load(f)

progress = 0.0
for feature in OSM_data['features']:
    print("Converting OSM features, progess: " + str(int(100*progress/len(OSM_data['features']))) + '%')
    progress+=1.0
    feature['geometry']['coordinates'] = get_vertices_of_feature(feature)
    for i in range(0, len(feature['geometry']['coordinates'])):
        point = feature['geometry']['coordinates'][i]
        feature['geometry']['coordinates'][i] = wgs84_to_epsg3006(point)
progress = 0.0
for feature in SLU_data['features']:
    print("Converting SLU features, progess: " + str(int(100*progress/len(SLU_data['features']))) + '%')
    progress+=1.0
    feature['geometry']['coordinates'] = get_vertices_of_feature(feature)
    for i in range(0, len(feature['geometry']['coordinates'])):
        point = feature['geometry']['coordinates'][i]
        feature['geometry']['coordinates'][i] = wgs84_to_epsg3006(point)

# Write all building features to files
with open('raw_data/osm_buildings_sweref.geojson', 'w') as f:
    dump(FeatureCollection(OSM_data), f)
with open('raw_data/slu_buildings_sweref.geojson', 'w') as f:
    dump(FeatureCollection(SLU_data), f)
