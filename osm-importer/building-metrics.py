# This script reads processed OSM and SLU building data, and finds the metrics specified in the project report
# REQUIREMENTS:
# - Run building-data-formatter.py
# - Run plot-shp-reader.py

from geojson import Point, Feature, FeatureCollection, load

OSM_data = {}
SLU_data = {}

def polygon_area(vertices):
    n = len(vertices) # of corners
    a = 0.0
    for i in range(n):
        j = (i + 1) % n
        a += abs(vertices[i][0] * vertices[j][1]-vertices[j][0] * vertices[i][1])
    result = a / 2.0
    return result

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

print("Finished loading map data")

# Metric: total building area
total_area_OSM = 0.0
total_area_SLU = 0.0
for feature in OSM_data['features']:
    total_area_OSM += polygon_area(get_vertices_of_feature(feature))
for feature in SLU_data['features']:
    total_area_SLU += polygon_area(get_vertices_of_feature(feature))
print(total_area_OSM)
print(total_area_SLU)
