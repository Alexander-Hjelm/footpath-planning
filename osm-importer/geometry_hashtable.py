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
        self.top_left_y = min_y

        dx = max_x - min_x
        dy = max_y - min_y

        px = dx - (dx % self.cell_size)
        py = dy - (dy % self.cell_size)

        cell_count_x = round(px / self.cell_size)+1
        cell_count_y = round(py / self.cell_size)+1

        hashtable = []
        for i in range(0, cell_count_x):
            hashtable.append([])
            for j in range(0, cell_count_y):
                hashtable[i].append([])

        # Add the feature to every hash bucket that its points belong to
        for feature in features:
            hashbuckets_added_to = []
            polygon = geometry_utils.extract_polygon_from_feature(feature)
            for point in polygon:
                x, y = self._get_hash_keys_of_point(point)
                if not hashtable[x][y] in hashbuckets_added_to:
                    hashtable[x][y].append(feature)
                    hashbuckets_added_to.append(hashtable[x][y])

        self.hashtable = hashtable

    def get_collision_canditates(self, feature):
        polygon = geometry_utils.extract_polygon_from_feature(feature)
        hash_coords = []
        for point in polygon:
            x, y = self._get_hash_keys_of_point(point)
            if not [x, y] in hash_coords: # Compare by value
                hash_coords.append([x, y])
        return self._get_features_in_bucket_surrounding(hash_coords)

    def _get_features_in_bucket_surrounding(self, x, y):
        return self._get_features_in_bucket_surrounding([x,y])

    def _get_features_in_bucket_surrounding(self, coords):
        features_out = []
        hash_coords = []
        for c in coords:
            x = int(c[0])
            y = int(c[1])

            for x_i in range(max(x-1, 0), min(x+2, len(self.hashtable))):
                for y_i in range(max(y-1, 0), min(y+2, len(self.hashtable[0]))):
                    if not [x, y] in hash_coords:
                        hash_coords.append([x,y])

        for c in hash_coords:
            # Don't add duplicate features
            features_got = self._get_features_in_bucket(c[0], c[1])
            for feature in features_got:
                if not feature in features_out:
                    features_out.append(feature)
        return features_out

    def _get_features_in_bucket(self, x, y):
        return self.hashtable[x][y]

    def _get_hash_keys_of_point(self, point):
        dx = point[0] - self.top_left_x
        dy = point[1] - self.top_left_y

        px = dx - (dx % self.cell_size)
        py = dy - (dy % self.cell_size)

        hx = round(px / self.cell_size)
        hy = round(py / self.cell_size)

        return hx, hy

