from geojson import Point, Feature, FeatureCollection, dump, load
import math
from queue import Queue

data_dir = "../osm-importer/raw_data/"
files_to_read = [
        "footpath.geojson",
        "residential.geojson",
        "secondary.geojson",
        "primary.geojson"
        ]
vertex_distance_threshold = 0.0002

class Node:
    x = 0.0
    y = 0.0
    neighbours = []

    def __init__(self, x, y):
        assert(isinstance(x, float))
        assert(isinstance(y, float))
        self.x = x
        self.y = y
        self.neighbours = []

    def distance_to(self, u):
        assert(isinstance(u, Node))
        return math.sqrt((self.x-u.x)**2 + (self.y-u.y)**2)

    def add_neighbour(self, u):
        assert(isinstance(u, Node))
        if not(u in self.neighbours):
            if not(u == self):
                self.neighbours.append(u)

class Patch:
    vertices = []

    def __init__(self, vertices):
        assert(isinstance(vertices, list))
        self.vertices = vertices

    def add_vertex(self, vertex):
        assert(isinstance(vertex, Node))
        self.vertices.append(vertex)

    def add_vertices(self, vertices_in):
        assert(isinstance(vertices_in, list))
        for vertex in vertices_in:
            self.add_vertex(vertex)

def Detect(G):
    #TODO: Not yet implemented, use this method to extract interesting features, such as circles
    return []

def Expand(patch):
    # Vertex processing queue
    Q = Queue()
    processed_vertices = []

    for vertex in patch.vertices:
        Q.put(vertex)
        processed_vertices.append(vertex)
    while Q.empty():
        v = Q.get()
        for u in v.neighbours:
            if not u in processed_vertices:
                    if v.distance_to(u) < vertex_distance_threshold:
                        patch.add_vertex(u)
                        Q.put(u)
                        processed_vertices.append(u)

def IsVertexInAnyPatch(vertex, patches):
    for patch in patches:
        if vertex in patch:
            return True
    return False

def ExtractPatches(G):
    patches = Detect(G)
    for patch in patches:
        Expand(patch)
    #TODO: Filter out intersections and expand them
    for vertex in G:
        if not IsVertexInAnyPatch(vertex, patches):
            patch = Patch([vertex])
            Expand(patch)
    #TODO: Go over all vertices v that are not in any patches. If a neighbour is in a patch, add v to that patch

for file_name in files_to_read:

    nodes_by_coord = {}

    # read file
    with open(data_dir + file_name, 'r') as f:
        data = load(f)
    print("Read geojson features from file: " + data_dir + file_name + "...")

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
                if node == nodes_by_coord[x_prev][y_prev]:
                    print("Error: Added the node as its own neighbour")
                node.add_neighbour(nodes_by_coord[x_prev][y_prev])
                nodes_by_coord[x_prev][y_prev].add_neighbour(node)

    G = []
    for x in nodes_by_coord:
        for y in nodes_by_coord[x]:
            G.append(nodes_by_coord[x][y])

    print("Extracting features from the dataset: " + file_name + "...")
    ExtractPatches(G)
