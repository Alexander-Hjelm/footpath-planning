# This script reads path data by highway type, infers weights and outputs collisions
# It requires that both OSM way data and OSM building data have been generated in SWEREF
# REQUIREMENTS:
# - Run way-convert-to-sweref.py
# - Run building-convert-to-sweref.py

import geometry_utils
import plot_utils
from geojson import Point, Feature, FeatureCollection, load
from geometry_hashtable import GeometryHashtable
from json import dump

highway_categories = [
        'footpath',
        'residential',
        'secondary',
        'primary'
        ]

standard_widths = {
        'footpath': 2.0,        # Measured range: 2.0m - 5.0m
        'residential': 6.0,     # Measured range: 6.0m - 9.0m
        'secondary': 6.5,       # Measured range: 7.0m - 16.0m
        'primary': 8.0          # Measured range: 8.0m - 10.0m
        }

way_data = {}
building_data = []

# read files
for hwy in highway_categories:
    with open('raw_data/' + hwy + '-converted.geojson', 'r') as f:
        way_data[hwy] = load(f)

with open('raw_data/buildings-osm-sweref.geojson', 'r') as f:
    building_data = load(f)

# Build polygon hashtables
print("Building hash tables...")
all_features_list = []
all_features_list += building_data['features']
for hwy in highway_categories:
    all_features_list += way_data[hwy]['features']

hashtable = GeometryHashtable("building-way-hashtable", 230)
hashtable.create_from_features_list(all_features_list)
print("Hash tables complete!")

# Store all found paths by street name
paths_by_name = {}
widths_by_id = {}

for hwy in way_data.keys():
    for feature in way_data[hwy]['features'] :
        # Skip tunnels
        if 'tunnel' in feature['properties'] and feature['properties']['tunnel'] == 'yes':
            continue

        # Set width to default
        feature.min_way_width = standard_widths[hwy]
        feature.max_way_width = 2*feature.min_way_width

        feature_collided = False

        for feature_2 in hashtable.get_collision_canditates(feature):
            if feature is feature_2:
                continue

            # Skip tunnels
            if 'tunnel' in feature_2['properties'] and feature_2['properties']['tunnel'] == 'yes':
                continue
            
            # Skip features that have already been handled
            if hasattr(feature_2, 'handled'):
                continue

            # Get polygons
            polygon_1 = geometry_utils.extract_polygon_from_feature(feature)
            polygon_2 = geometry_utils.extract_polygon_from_feature(feature_2)

            # Get edges
            for i in range(0, len(polygon_1)-1):
                edge_1 = [polygon_1[i], polygon_1[i+1]]
                for j in range(0, len(polygon_2)-1):
                    edge_2 = [polygon_2[j], polygon_2[j+1]]

                    shortest_dist, closest_node = geometry_utils.shortest_distance_between_edges_projected(edge_1, edge_2)
                    if shortest_dist == None:
                        continue

                    # For two roads, move on if the distance is 0 (meaning adjoining roads or intersections)
                    if 'highway' in feature['properties'] and 'highway' in feature_2['properties']:
                        if shortest_dist == 0.0:
                            continue
                    
                    #print("Shortest dist was not None! It was: " + str(shortest_dist))
                    #plot_utils.plot_polygons([polygon_1, polygon_2])
                    if shortest_dist < feature.min_way_width:
                        print("Features collision!")
                        print(feature)
                        print(feature_2)
                        print("min dist: " + str(feature.min_way_width))
                        print("************")
                        #plot_utils.plot_polygons([polygon_1, polygon_2])
                    else:
                        feature.max_way_width = min(feature.max_way_width, shortest_dist)

        feature.handled = True
        if feature_collided:
            stat_collision_feature_count += 1

    break

#TODO: Printa statistik: antal kolliderande features, antal kolliderande noder (#/%)
#TODO: Printa statistik: längd av kolliderande väg, total längd
