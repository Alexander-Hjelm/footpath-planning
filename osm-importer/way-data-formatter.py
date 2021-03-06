# This script reads a raw Overpass Turbo export file with paths and processes it,
# Filtering accepted highway types and creates an output file for wach accepted highway type.
# Run it first with the raw Overpass Turbo data before doing anything else!
# REQUIREMENTS:
# - ./raw_data/export.geojson

from geojson import Point, Feature, FeatureCollection, dump, load

accepted_highways = [
        'pedestrian',
        'footway',
        'path',
        'tertiary',
        'tertiary_link',
        'secondary',
        'secondary_link',
        'primary',
        'primary_link',
        'residential']
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
        'residential': ['residential'],
        'secondary': ['tertiary', 'tertiary_link'],
        'primary': ['primary', 'primary_link', 'secondary', 'secondary_link']}

# read file
with open('raw_data/export.geojson', 'r') as f:
    data = load(f)

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
        dump(FeatureCollection(data_out[highway]), f)
        


