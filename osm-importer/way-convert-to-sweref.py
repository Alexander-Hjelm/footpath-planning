# Coverts processed OSM way data to sweref coordinates
# REQUIREMENTS:
# - Run way-data-formatter.py

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

highway_categories = ['footpath', 'residential', 'secondary', 'primary']

way_data = {}

print("Reading files...")

# Read files
for hwy in highway_categories:
    with open('raw_data/' + hwy + '.geojson', 'r') as f:
        way_data[hwy] = load(f)

total_len = 0
total_progress = 0
for hwy in highway_categories:
    total_len += len(way_data[hwy]['features'])

print("Total number of features to convert: " + str(total_len))

# Conversion run
for hwy in highway_categories:
    print("Number of " + hwy + " features to convert: " + str(len(way_data[hwy]['features'])))
    progress = 0
    for feature in way_data[hwy]['features']:
        step_recursively(feature['geometry']['coordinates'])
        # Progress
        print("Converting " + hwy + " features, progess: " + str(progress) + "/" + str(len(way_data[hwy]['features'])) + " | Total progress: " + str(100*total_progress/total_len) + "%")
        progress+=1
        total_progress+=1

# Write all building features to files
for highway in highway_categories:
    with open('raw_data/' + highway + '-converted.geojson', 'w') as f:
        dump(FeatureCollection(way_data[highway]), f)
