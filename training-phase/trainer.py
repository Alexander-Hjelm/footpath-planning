from geojson import Point, Feature, FeatureCollection, load
from json import dump
import math
from queue import Queue

data_dir = "../osm-importer/raw_data/"
files_to_read = [
        "footpath",
        "residential",
        "secondary",
        "primary"
        ]
vertex_distance_threshold = 0.0002
min_num_of_vertices_per_patch = 2

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
    edges = []

    # Statistical paramteres, Nishida et. al, section 4.2
    stat_len = 0.0      # Average edge length
    stat_len_var = 0.0  # Variance, edge length
    stat_curv = 0.0     # Average edge curvature
    stat_curv_var = 0.0 # Variance, edge curvature

    def __init__(self, vertex):
        assert(isinstance(vertex, Node))
        self.vertices = [vertex]
        self.edges = []

    def add_vertex(self, vertex):
        assert(isinstance(vertex, Node))
        self.vertices.append(vertex)
        u_index = len(self.vertices)-1
        for neighbour in vertex.neighbours:
            if neighbour in self.vertices:
                v_index = self.vertices.index(neighbour)
                self.edges.append([u_index, v_index])

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
        if vertex in patch.vertices:
            return True
    return False

def ExtractPatches(G):
    # Filter out interesting features and expand them
    patches = Detect(G)
    for patch in patches:
        Expand(patch)

    # For the remaining graph, filter out intersections and expand them
    for vertex in G:
        if not IsVertexInAnyPatch(vertex, patches):
            if len(vertex.neighbours) > 2:
                patch = Patch(vertex)
                patches.append(patch)
                Expand(patch)

    # Go over all vertices remaining vertices v. If a neighbour is in a patch, add v to that patch
    G_unassigned = Queue()
    for vertex in G:
        if not IsVertexInAnyPatch(vertex, patches):
            G_unassigned.put(vertex)
    i = 0
    max_iterations = int(len(G)*2.0)
    while not G_unassigned.empty():
        v = G_unassigned.get()
        patch_was_found = False
        for u in v.neighbours:
            for patch in patches:
                if u in patch.vertices:
                    patch.add_vertex(v);
                    patch_was_found = True
                    break
            if patch_was_found:
                break
        if not patch_was_found:
            G_unassigned.put(v)

        if i == max_iterations:
            break
        i += 1

    return patches


for file_name in files_to_read:

    nodes_by_coord = {}

    # read file
    with open(data_dir + file_name + '.geojson', 'r') as f:
        data = load(f)
    print("Read geojson features from file: " + data_dir + file_name + ".geojson...")

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
    patches = ExtractPatches(G)
    json_out = []
    i = 0
    for patch in patches:
        if len(patch.vertices) < min_num_of_vertices_per_patch:
            continue
        json_out.append({})
        json_out[i]['edges'] = []
        json_out[i]['points'] = []
        for v in patch.vertices:
            json_out[i]['points'].append([v.x, v.y])
        for e in patch.edges:
            # Add the edge to the ouput json object
            json_out[i]['edges'].append([e[0], e[1]])
            if e[0] > len(patch.vertices):
                print("ERROR")
        i += 1

    with open('out_data/' + file_name + '.json', 'w') as f:
        dump(json_out, f)

