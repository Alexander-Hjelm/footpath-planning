import pickle
import math
import geometry_utils

class GeometryHashtable:

    name = None
    hashtable = None
    cell_size = None
    top_left_x = None
    top_left_y = None

    def __init__(self, name, cell_size):
        self.name = name
        self.cell_size = cell_size

    def create_from_polygons_list(self, polygons):
        min_x, min_y, max_x, max_y = geometry_utils.minmax_points_of_polygons(polygons)
        x_d = max_x - min_x
        y_d = max_y - min_y
        cell_count_x = math.ceil(x_d/cell_size)
        cell_count_y = meah.ceil(y_d/cell_size)
        hashtable = []
        for i in range(0, cell_count_x):
            hashtable.append([])
            for j in range(0, cell_count_y):
                hashtable[i].append([])

        for polygon in polygons:
            x, y = _get_hash_keys_of_polygon(polygon)
            hashtable[x][y] = polygon

        self.hashtable = hashtable

    def get_collision_canditates(self, polygon):
        x, y = _get_hash_keys_of_polygon(polygon)
        return _get_polygons_in_bucket_surrounding(x, y)

    def write_hashtable_to_file(self):
        with open('geometry-hashtable-' + name, 'wb') as fp:
            pickle.dump(self.hashtable, fp)

    def load_hashtable_from_file(self):
        with open ('geometry-hashtable-' + name, 'rb') as fp:
            self.hashtable = pickle.load(fp)

    def _get_polygons_in_bucket_surrounding(self, x, y):
        polygons_out = []
        for x_i in range(x-1, x+2):
            for y_i in range(y-1, y+2):
                polygons_out += self._get_polygons_in_bucket(x_i, y_i)
        return polygons_out

    def _get_polygons_in_bucket(self, x, y):
        return self.hashtable[x][y]

    def _get_hash_keys_of_polygon(self, polygon):
        center = geometry_utils.polygon_centroid(polygon)
        x = (center[0]-top_left_x)/cell_size
        y = (center[1]-top_left_y)/cell_size
        return round(x), round(y)

