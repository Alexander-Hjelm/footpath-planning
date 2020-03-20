# Coverts processed data to a simple geometric structure
# This overwrites the files buildings-xxx.geojson, be careful!
# REQUIREMENTS:
# - Run building-data-formatter-osm.py
# - Run building-data-formatter-slu.py

from geojson import Point, Feature, FeatureCollection, load, dump

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
with open('raw_data/buildings-osm.geojson', 'r') as f:
    OSM_data = load(f)
with open('raw_data/buildings-slu.geojson', 'r') as f:
    SLU_data = load(f)

progress = 0.0
for feature in OSM_data['features']:
    feature['geometry']['coordinates'] = get_vertices_of_feature(feature)
progress = 0.0
for feature in SLU_data['features']:
    feature['geometry']['coordinates'] = get_vertices_of_feature(feature)

# Write all building features to files
with open('raw_data/buildings-osm.geojson', 'w') as f:
    dump(FeatureCollection(OSM_data), f)
with open('raw_data/buildings-slu.geojson', 'w') as f:
    dump(FeatureCollection(SLU_data), f)
