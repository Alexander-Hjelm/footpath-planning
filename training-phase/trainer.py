from geojson import Point, Feature, FeatureCollection, dump, load

data_dir = "../osm-importer/raw_data/"
files_to_read = [
        "footpath.geojson",
        "residential.geojson",
        "secondary.geojson",
        "primary.geojson"
        ]

for file_name in files_to_read:

    # read file
    with open(data_dir + file_name, 'r') as f:
        data = load(f)
    print(data)
