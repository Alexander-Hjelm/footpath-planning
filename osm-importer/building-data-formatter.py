from geojson import Point, Feature, FeatureCollection, dump, load

accepted_types = [
        'Polygon'
        ]
rejected_types = [
        'Point'
        ]

# read file
with open('raw_data/export-buildings.geojson', 'r') as f:
    data = load(f)

data_out = []

# Filter out points, only keep Polygons and MultiPolygons
for feature in data['features'] :
    geometry = feature['geometry']
    if 'type' in geometry:
        if geometry['type'] in accepted_types:
            data_out.append(feature)
            continue
        elif geometry['type'] in rejected_types:
            continue

    print("[WARNING] Found a feature that was not caught by the filter: \n" + str(feature) + ", add handling for this feature!")

# Write all building features to files
with open('raw_data/buildings.geojson', 'w') as f:
    dump(FeatureCollection(data_out), f)

