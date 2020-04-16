# This script reads path data by highway type, infers weights and outputs collisions
# It requires that both OSM way data and OSM building data have been generated in SWEREF
# REQUIREMENTS:
# - Run way-convert-to-sweref.py
# - Run building-convert-to-sweref.py

from geojson import Point, Feature, FeatureCollection, load
from json import dump

highway_categories = [
        'footpath',
        'residential',
        'secondary',
        'primary'
        ]

standard_widths = {
        'footpath': 2.0,        # Measured range: 2.0m - 5.0m
        'residential': 6.0,     # Measured range: 6.0m - 9.0m
        'secondary': 6.5,       # Measured range: 7.0m - 16.0m
        'primary': 8.0          # Measured range: 8.0m - 10.0m
        }

way_data = {}
building_data = []

# read files
for hwy in highway_categories:
    with open('raw_data/' + hwy + '-converted.geojson', 'r') as f:
        way_data[hwy] = load(f)

with open('raw_data/buildings-osm-sweref.geojson', 'r') as f:
    building_data = load(f)

all_features_list = []
all_features_list += building_data['features']
for hwy in highway_categories:
    all_features_list.append(way_data[hwy]['features'])

# Build polygon hashtables
print("Building hash tables...")
hashtable = GeometryHashtable("building-way-hashtable", 230)
hashtable.create_from_features_list(all_features_list)
print("Hash tables complete!")

# Store all found paths by street name
paths_by_name = {}
widths_by_id = {}

for hwy in way_data.keys():
    for feature in way_data[hwy]['features'] :
        # Set width to default
        feature.way_width = standard_widths[hwy]
