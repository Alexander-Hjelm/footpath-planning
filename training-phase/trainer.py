# This script takes the generated road network and generates patches
# for use in the example-based geneation phase.
# REQUIREMENTS:
# - Run way-data-formatter.py

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
    associated_path = ""

    def __init__(self, x, y, associated_path):
        assert(isinstance(x, float))
        assert(isinstance(y, float))
        self.x = x
        self.y = y
        self.neighbours = []
        self.associated_path = associated_path

    def distance_to(self, u):
        assert(isinstance(u, Node))
        return math.sqrt((self.x-u.x)**2 + (self.y-u.y)**2)

    def add_neighbour(self, u):
        assert(isinstance(u, Node))
        if not(u in self.neighbours):
            if not(u == self):
                self.neighbours.append(u)

    def get_neighbours_of_same_path(self):
        out = []
        for v in self.neighbours:
            if v.associated_path == self.associated_path:
                out.append(v)
        return out

    def nomarlized(self):
        d = self.magnitude()
        return Node(x/d, y/d, self.associated_path)

    def magnitude(self):
        return math.sqrt((self.x)**2 + (self.y)**2)

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

        self.stat_len = 0.0
        self.stat_len_var = 0.0
        self.stat_curv = 0.0
        self.stat_curv_var = 0.0

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

    def calculate_statistical_params(self):
        edge_count = len(self.edges)
        avg_len = 0.0
        var_len = 0.0
        avg_curv = 0.0
        var_curv = 0.0
        stored_lens = []
        stored_curvs = []

        # Edge length, average
        for e in self.edges:
            u = self.vertices[e[0]]
            v = self.vertices[e[1]]
            res = u.distance_to(v)
            avg_len += res
            stored_lens.append(res)

        if len(stored_lens) > 0:
            avg_len /= len(stored_lens)

            # Edge length, variance
            for d in stored_lens:
                var_len += (avg_len - d)**2
            var_len /= edge_count
        else:
            avg_len = -1.0
            var_len = -1.0

        # Edge curvature, average
        for vertex in self.vertices:
            neighbours = vertex.get_neighbours_of_same_path()
            if len(neighbours) > 1:
                u = neighbours[0]
                v = neighbours[1]
                if vertex.associated_path == u.associated_path and vertex.associated_path == v.associated_path:
                    z_1 = Node(u.x-vertex.x, u.y-vertex.y, "")
                    z_2 = Node(vertex.x-v.x, vertex.y-v.y, "")
                    nom = z_1.nomarlized().distance_to(z_2.nomarlized())
                    denom = z_1.magnitude()
                    res = nom/denom
                    avg_curv += res
                    stored_curvs.append(res)

        if len(stored_curvs) > 0:
            avg_curv /= len(stored_curvs)

            # Edge curvature, variance
            for k in stored_curvs:
                var_curv += (avg_curv - k)**2
            var_curv /= len(stored_curvs)
        else:
            avg_curv = -1.0
            var_curv = -1.0

        self.stat_len = avg_len
        self.stat_len_var = var_len
        self.stat_curv = avg_curv
        self.stat_curv_var = var_curv



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
    while not Q.empty():
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

    # Finally, compute statistical parameters for all patches
    for patch in patches:
        patch.calculate_statistical_params()

    return patches

id_map = {}

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
        feature_id = properties['@id']

        # Skip polygon features
        if geo_type == 'Polygon' or geo_type == "MultiPolygon":
            continue

        coordinates = geometry['coordinates']
        for i in range(0, len(coordinates)):
            coordinate = coordinates[i]
            x = coordinate[0]
            y = coordinate[1]

            node = Node(x, y, feature_id)

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
                node_prev = nodes_by_coord[x_prev][y_prev]
                node.add_neighbour(node_prev)
                nodes_by_coord[x_prev][y_prev].add_neighbour(node)
                # Register the neighbour relationship with the feature id
                if not node in id_map:
                    id_map[node] = {}
                if not node_prev in id_map:
                    id_map[node_prev] = {}
                id_map[node][node_prev] = feature_id
                id_map[node_prev][node] = feature_id

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
        json_out[i]['points'] = []
        json_out[i]['edges'] = []
        json_out[i]['edge_ids'] = []
        json_out[i]['stat_avg_len'] = patch.stat_len
        json_out[i]['stat_var_len'] = patch.stat_len_var
        json_out[i]['stat_avg_curv'] = patch.stat_curv
        json_out[i]['stat_var_curv'] = patch.stat_curv_var
        for v in patch.vertices:
            json_out[i]['points'].append([v.x, v.y])
        for e in patch.edges:
            # Add the edge to the ouput json object
            json_out[i]['edges'].append([e[0], e[1]])
            if e[0] > len(patch.vertices):
                print("ERROR")
            json_out[i]['edge_ids'].append(id_map[patch.vertices[e[0]]][patch.vertices[e[1]]])
        i += 1

    with open('out_data/' + file_name + '.json', 'w') as f:
        dump(json_out, f)

