from geojson import Point, Feature, FeatureCollection, dump, load

data_dir = "../osm-importer/raw_data/"
files_to_read = [
        "footpath.geojson",
        "residential.geojson",
        "secondary.geojson",
        "primary.geojson"
        ]

class Node:
    x = 0.0
    y = 0.0
    neighbours = []

    def __init__(self, x, y):
        self.x = x
        self.y = y

for file_name in files_to_read:

    nodes_by_coord = {}

    # read file
    with open(data_dir + file_name, 'r') as f:
        data = load(f)

    for feature in data['features'] :
        properties = feature['properties']
        geometry = feature['geometry']
        geo_type = geometry['type']

        # Skip polygon features
        if geo_type == 'Polygon' or geo_type == "MultiPolygon":
            continue

        coordinates = geometry['coordinates']
        for i in range(0, len(coordinates)):
            coordinate = coordinates[i]
            x = coordinate[0]
            y = coordinate[1]

            node = Node(x, y)

            # Add node to dictionary if not already read
            if not x in nodes_by_coord:
                nodes_by_coord[x] = {}
            if not y in nodes_by_coord[x]:
                nodes_by_coord[x][y] = node

            if i > 0:
                x_prev = coordinates[i-1][0]
                y_prev = coordinates[i-1][1]
                node.neighbours.append(nodes_by_coord[x_prev][y_prev])
                nodes_by_coord[x_prev][y_prev].neighbours.append(node)
