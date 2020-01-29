import json

accepted_highways = [
        'pedestrian',
        'footway',
        'path',
        'tertiary',
        'tertiary_link',
        'secondary',
        'secondary_link',
        'primary',
        'primary_link']
rejected_highways = [
        'crossing',
        'elevator',
        'traffic_signals',
        'give_way',
        'bus_stop',
        'motorway_junction',
        'steps',
        'service',
        'platform',
        'unclassified',
        'trunk',
        'trunk_link',
        'residential',
        'turning_circle',
        'corridor',
        'cycleway',
        'corridor',
        'disused',
        'track',
        'escalator',
        'living_street',
        'bridleway',
        'motorway_link',
        'proposed',
        'construction',
        'mini_roundabout']

highway_categories = {
        'footpath': ['pedestrian', 'footway', 'path'],
        'tertiary': ['tertiary', 'tertiary_link'],
        'secondary': ['secondary', 'secondary_link'],
        'primary': ['primary', 'primary_link']}

# read file
with open('raw_data/export.geojson', 'r') as f:
    datastring=f.read()

data = json.loads(datastring)
data_out = {}

for highway in highway_categories:
    data_out[highway] = []

for feature in data['features'] :
    properties = feature['properties']
    if 'highway' in properties:
        highway = properties['highway']

        if highway in accepted_highways:
            for hw_category in highway_categories.keys():
                if highway in highway_categories[hw_category]:
                    data_out[hw_category].append(feature)

        # Error printing
        if not highway in accepted_highways:
            if not highway in rejected_highways:
                print("[WARNING] Found a highway of type: " + highway + ", add handling for this road type!")

# Write all highway categories to files
for highway in highway_categories:
    with open('raw_data/' + highway + '.geojson', 'w') as f:
        json.dump(data_out[highway], f)
        


