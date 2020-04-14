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
    with open('raw_data/' + hwy + '.geojson', 'r') as f:
        way_data[hwy] = load(f)

with open('raw_data/buildings-osm-sweref.geojson', 'r') as f:
    building_data = load(f)


# Store all found paths by street name
paths_by_name = {}
widths_by_id = {}

for hwy in way_data.keys():
    for feature in way_data[hwy]['features'] :
        properties = feature['properties']

        # Set width to default
        widths_by_id[properties['@id']] = standard_widths[hwy]

        # Identify features with same name and store them together
        if 'name' in properties:
            name = properties['name']

            if not name in paths_by_name:
                paths_by_name[name] = []
            paths_by_name[name].append(feature)
        else:
            print("[WARNING] The following way did not have a name:\n" + str(feature))

# Write all paths widths to file
with open('raw_data/path_widths.json', 'w') as f:
    dump(widths_by_id, f)
        
