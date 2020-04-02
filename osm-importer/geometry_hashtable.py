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

    def create_from_features_list(self, features):
        min_x, min_y, max_x, max_y = geometry_utils.extents_of_features(features)

        self.top_left_x = min_x
        self.top_left_y = max_y

        dx = max_x - min_x
        dy = max_y - min_y

        px = dx - (dx % self.cell_size)
        py = dy - (dy % self.cell_size)

        cell_count_x = round(px / self.cell_size)
        cell_count_y = round(py / self.cell_size)

        hashtable = []
        for i in range(0, cell_count_x):
            hashtable.append([])
            for j in range(0, cell_count_y):
                hashtable[i].append([])

        for feature in features:
            x, y = self._get_hash_keys_of_feature(feature)
            hashtable[x][y].append(feature)

        self.hashtable = hashtable

    def get_collision_canditates(self, feature):
        x, y = self._get_hash_keys_of_feature(feature)
        return _get_features_in_bucket_surrounding(x, y)

    def _get_features_in_bucket_surrounding(self, x, y):
        features_out = []
        for x_i in range(x-1, x+2):
            for y_i in range(y-1, y+2):
                features_out += self._get_features_in_bucket(x_i, y_i)
        return features_out

    def _get_features_in_bucket(self, x, y):
        return self.hashtable[x][y]

    def _get_hash_keys_of_feature(self, feature):
        polygon = geometry_utils.extract_polygon_from_feature(feature)
        center = geometry_utils.polygon_centroid(polygon)
        dx = center[0] - self.top_left_x
        dy = center[1] - self.top_left_y

        px = dx - (dx % self.cell_size)
        py = dy - (dy % self.cell_size)

        hx = round(px / self.cell_size)
        hy = round(py / self.cell_size)

        return hx, hy

