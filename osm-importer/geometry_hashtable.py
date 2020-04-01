import pickle

class GeometryHashtable:

    name = None
    hashtable = None

    def __init(self, name):
        # Load a hashtable from file
        self.name = name
        _load_hashtable_from_file()

    def __init__(self, name, polygons, cell_size, top_left_x, top_left_y):
        # Create a hashtable from a list of polygons and save it to file
        self.name = name
        self.hashtable = self._create_hashtable_from_polygons(polygons)
        _write_hashtable_to_file()

    def get_polygons_in_bucket_surrounding(x, y):
        pass

    def get_polygons_in_bucket(x, y):
        pass

    def get_hash_keys_of_point(x, y):
        pass

    def _create_hashtable_from_polygons(polygons):
        pass

    def _write_hashtable_to_file():
        with open('geometry-hashtable-' + name, 'wb') as fp:
            pickle.dump(hashtable, fp)

    def _load_hashtable_from_file():
        with open ('geometry-hashtable-' + name, 'rb') as fp:
            hashtable = pickle.load(fp)

