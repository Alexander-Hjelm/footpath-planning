# This script reads path data by highway type, and outputs a file with the width of every street by id
# It requires that way-data-formatter.py has been run first to generate the neccessary road files.
# REQUIREMENTS:
# - Run way-data-formatter.py

from geojson import Point, Feature, FeatureCollection, load
from json import dump

highway_categories = [
        'footpath',
        'residential',
        'secondary',
        'primary'
        ]

standard_widths = {
        'footpath': 0.25,
        'residential': 0.5,
        'secondary': 0.75,
        'primary': 1.0
        }

path_data = {}

# read files
for hwy in highway_categories:
    with open('raw_data/' + hwy + '.geojson', 'r') as f:
        path_data[hwy] = load(f)

# Store all found paths by street name
paths_by_name = {}
widths_by_id = {}

for hwy in path_data.keys():
    for feature in path_data[hwy]['features'] :
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
        
