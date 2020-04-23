# This script reads path data by highway type, infers weights and outputs collisions
# It requires that both OSM way data and OSM building data have been generated in SWEREF
# REQUIREMENTS:
# - Run way-convert-to-sweref.py
# - Run building-convert-to-sweref.py

import geometry_utils
import plot_utils
import pickle
import numpy as np
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

stat_collision_feature_count = {}
stat_collision_node_count = {}
stat_collision_edge_len = {}
stat_total_features_count = {}
stat_total_node_count = {}
stat_total_edge_len = {}
total_total_features_count = 0
colliding_features_tentative = []

for hwy in highway_categories:
    total_total_features_count += len(way_data[hwy]['features'])
    stat_collision_feature_count[hwy] = 0
    stat_collision_node_count[hwy] = 0
    stat_collision_edge_len[hwy] = 0.0
    stat_total_features_count[hwy] = 0
    stat_total_node_count[hwy] = 0
    stat_total_edge_len[hwy] = 0.0

# Set way default widths per features
for hwy in way_data.keys():
    for feature in way_data[hwy]['features'] :
        feature.min_way_width = standard_widths[hwy]
        feature.max_way_width = 2*feature.min_way_width

# Collision detection

progress = 0.0
for hwy in way_data.keys():
    for feature in way_data[hwy]['features'] :
        # Skip tunnels
        if 'tunnel' in feature['properties'] and feature['properties']['tunnel'] == 'yes':
            continue

        print("Feature collision check, progess: " + str(100*progress/total_total_features_count) + '%')
        progress+=1.0

        stat_total_features_count[hwy] += 1

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
                stat_total_node_count[hwy] += 1
                stat_total_edge_len[hwy] += geometry_utils.point_distance(edge_1[0], edge_1[1])
                for j in range(0, len(polygon_2)-1):
                    edge_2 = [polygon_2[j], polygon_2[j+1]]

                    shortest_dist, closest_node = geometry_utils.shortest_distance_between_edges_projected(edge_1, edge_2)
                    if shortest_dist == None:
                        continue

                    # For two roads, move on if the distance is 0 (meaning adjoining roads or intersections)
                    if 'highway' in feature['properties'] and 'highway' in feature_2['properties']:
                        if shortest_dist == 0.0:
                            continue
                    
                    #plot_utils.plot_polygons([polygon_1, polygon_2])
                    collision = False
                    if 'highway' in feature_2['properties']:
                        # If the other feature is a path, factor in its road width
                        collision = shortest_dist < feature.min_way_width + feature_2.min_way_width
                    else:
                        collision = shortest_dist < feature.min_way_width

                    if collision:
                        stat_collision_node_count[hwy] += 1

                        if not feature in colliding_features_tentative:
                            colliding_features_tentative.append(feature)
                        if 'highway' in feature_2['properties'] and not feature_2 in colliding_features_tentative:
                            colliding_features_tentative.append(feature_2)

                        if closest_node == polygon_1[0]:
                            stat_collision_edge_len[hwy] += geometry_utils.point_distance(polygon_1[0], polygon_1[1]) / 2
                        elif closest_node == polygon_1[-1]:
                            stat_collision_edge_len[hwy] += geometry_utils.point_distance(polygon_1[-2], polygon_1[-1]) / 2
                        else:
                            index = polygon_1.index(closest_node)
                            stat_collision_edge_len[hwy] += geometry_utils.point_distance(polygon_1[index-1], polygon_1[index]) / 2
                            stat_collision_edge_len[hwy] += geometry_utils.point_distance(polygon_1[index], polygon_1[index+1]) / 2

                        feature_collided = True

                        """
                        if 'highway' in feature_2['properties']:
                            plot_utils.plot_edges([polygon_2, polygon_1])
                        else:
                            plot_utils.plot_polygons_and_edges([polygon_2], polygon_1)
                        """
                    else:
                        feature.max_way_width = min(feature.max_way_width, shortest_dist)

        feature.handled = True
        if feature_collided:
            stat_collision_feature_count[hwy] += 1

print("Collision correction...")

# Collision correction
# Collision correction: Store collided features in a tentative map. When a collision is fixed, add both feature_1 and feature_2 to the tentative map
reached_stable = False
while not reached_stable:
    reached_stable = True

    feature_1 = colliding_features_tentative.pop(0)
    polygon_1 = geometry_utils.extract_polygon_from_feature(feature_1)
    for feature_2 in hashtable.get_collision_canditates(feature):
        if feature is feature_2:
            continue
        polygon_2 = geometry_utils.extract_polygon_from_feature(feature_2)
    
        for i in range(0, len(polygon_1)-1):
            edge_1 = [polygon_1[i], polygon_1[i+1]]
            for j in range(0, len(polygon_2)-1):
                edge_2 = [polygon_2[j], polygon_2[j+1]]

                shortest_dist, closest_node = geometry_utils.shortest_distance_between_edges_projected(edge_1, edge_2)

                if shortest_dist == None:
                    continue

                # Skip tunnels
                if 'tunnel' in feature_2['properties'] and feature_2['properties']['tunnel'] == 'yes':
                    continue

                # For two roads, move on if the distance is 0 (meaning adjoining roads or intersections)
                if 'highway' in feature['properties'] and 'highway' in feature_2['properties']:
                    if shortest_dist == 0.0:
                        continue

                collision = False
                if 'highway' in feature_2['properties']:
                    # If the other feature is a path, factor in its road width
                    collision = shortest_dist < feature.min_way_width + feature_2.min_way_width
                else:
                    collision = shortest_dist < feature.min_way_width

                if collision:
                    # Feature correction by relaxing both edges in the opposite direction
                    perp_1 = geometry_utils.perpendicular([edge_1[1][0]-edge_1[0][0], edge_1[1][1]-edge_1[0][1]])
                    perp_2 = geometry_utils.perpendicular([edge_2[1][0]-edge_2[0][0], edge_2[1][1]-edge_2[0][1]])
                    perp_1 = geometry_utils.normalize(perp_1)
                    perp_2 = geometry_utils.normalize(perp_2)

                    translation_vec = None
                    if np.dot(perp_1, perp_2) > np.dot(perp_1, -perp_2):
                        translation_vec = [perp_1[0]+perp_2[0], perp_1[1]+perp_2[1]]
                    else:
                        translation_vec = [perp_1[0]-perp_2[0], perp_1[1]-perp_2[1]]

                    translation_vec = geometry_utils.normalize(translation_vec)
                    translation_dist = shortest_dist/2

                    edge_1_tr_1 = []
                    edge_2_tr_1 = []
                    edge_1_tr_2 = []
                    edge_2_tr_2 = []

                    edge_1_tr_1[0] = edge_1[0] + translation_vec[0]*translation_dist
                    edge_1_tr_1[1] = edge_1[1] + translation_vec[1]*translation_dist
                    edge_2_tr_1[0] = edge_2[0] - translation_vec[0]*translation_dist
                    edge_2_tr_1[1] = edge_2[1] - translation_vec[1]*translation_dist

                    edge_1_tr_2[0] = edge_1[0] - translation_vec[0]*translation_dist
                    edge_1_tr_2[1] = edge_1[1] - translation_vec[1]*translation_dist
                    edge_2_tr_2[0] = edge_2[0] + translation_vec[0]*translation_dist
                    edge_2_tr_2[1] = edge_2[1] + translation_vec[1]*translation_dist

                    matching_1 = geometry_utils.min_edge_endpoints_matching(edge_1_tr_1, edge_2_tr_1)
                    matching_2 = geometry_utils.min_edge_endpoints_matching(edge_1_tr_2, edge_2_tr_2)
                    avg_dist_1 = geometry_utils.point_distance(matching_1[0][0], matching_1[0][1]) + geometry_utils.point_distance(matching_1[1][0], matching_1[1][1])
                    avg_dist_2 = geometry_utils.point_distance(matching_2[0][0], matching_2[0][1]) + geometry_utils.point_distance(matching_2[1][0], matching_2[1][1])
                    if avg_dist_1 > avg_dist_2:
                        edge_1 = edge_1_tr_1
                        edge_2 = edge_2_tr_1
                    else:
                        edge_1 = edge_1_tr_2
                        edge_2 = edge_2_tr_2

                    # If a collision was fixed, queue this feature again and continue lates
                    colliding_features_tentative.append(feature_1)
                    reached_stable = False

# Collect statistics after correction run
print("Statistics collection...")

stat_corrected_collision_feature_count = {}
stat_corrected_collision_node_count = {}
stat_corrected_collision_edge_len = {}

for hwy in highway_categories:
    stat_corrected_collision_feature_count[hwy] = 0
    stat_corrected_collision_node_count[hwy] = 0
    stat_corrected_collision_edge_len[hwy] = 0.0

# Mark all features as unhandled
for hwy in way_data.keys():
    for feature in way_data[hwy]['features']:
        feature.handled = False

for feature in building_data['features']:
    feature.handled = False

progress = 0.0
for hwy in way_data.keys():
    for feature in way_data[hwy]['features'] :
        # Skip tunnels
        if 'tunnel' in feature['properties'] and feature['properties']['tunnel'] == 'yes':
            continue

        print("Feature collision check, progess: " + str(100*progress/total_total_features_count) + '%')
        progress+=1.0

        feature_collided = False

        for feature_2 in hashtable.get_collision_canditates(feature):
            if feature is feature_2:
                continue

            # Skip tunnels
            if 'tunnel' in feature_2['properties'] and feature_2['properties']['tunnel'] == 'yes':
                    continue

            # Skip features that have alreay been handled
            if feature_2.handled:
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
                    
                    #plot_utils.plot_polygons([polygon_1, polygon_2])
                    collision = False
                    if 'highway' in feature_2['properties']:
                        # If the other feature is a path, factor in its road width
                        collision = shortest_dist < feature.min_way_width + feature_2.min_way_width
                    else:
                        collision = shortest_dist < feature.min_way_width

                    if collision:
                        stat_corrected_collision_node_count[hwy] += 1

                        if closest_node == polygon_1[0]:
                            stat_corrected_collision_edge_len[hwy] += geometry_utils.point_distance(polygon_1[0], polygon_1[1]) / 2
                        elif closest_node == polygon_1[-1]:
                            stat_corrected_collision_edge_len[hwy] += geometry_utils.point_distance(polygon_1[-2], polygon_1[-1]) / 2
                        else:
                            index = polygon_1.index(closest_node)
                            stat_corrected_collision_edge_len[hwy] += geometry_utils.point_distance(polygon_1[index-1], polygon_1[index]) / 2
                            stat_corrected_collision_edge_len[hwy] += geometry_utils.point_distance(polygon_1[index], polygon_1[index+1]) / 2

                        feature_collided = True

        feature.handled = True
        if feature_collided:
            stat_corrected_collision_feature_count[hwy] += 1

statistics_dict = {}

statistics_dict['stat_collision_feature_count'] = stat_collision_feature_count
statistics_dict['stat_total_feature_count'] = stat_total_features_count
statistics_dict['stat_collision_node_count'] = stat_collision_node_count
statistics_dict['stat_total_node_count'] = stat_total_node_count
statistics_dict['stat_collision_edge_len'] = stat_collision_edge_len
statistics_dict['stat_total_edge_len'] = stat_total_edge_len
statistics_dict['stat_corrected_collision_feature_count'] = stat_corrected_collision_feature_count
statistics_dict['stat_corrected_collision_node_count'] = stat_corrected_collision_node_count
statistics_dict['stat_corrected_collision_edge_len'] = stat_corrected_collision_edge_len

with open('way-collision-statistics', 'wb') as fp:
    pickle.dump(statistics_dict, fp)

# Results
print("Results...")
for hwy in highway_categories:
    print("****************")
    print(hwy)
    print("****************")
    print("Pre correction")
    print("----------------")
    print("Colliding features count: " + str(stat_collision_feature_count[hwy]))
    print("Colliding nodes count: " + str(stat_collision_node_count[hwy]))
    print("Colliding edges cumulative length: " + str(stat_collision_edge_len[hwy]))

    print("Total features count: " + str(stat_total_features_count[hwy]))
    print("Total nodes count: " + str(stat_total_node_count[hwy]))
    print("Total edges cumulative length: " + str(stat_total_edge_len[hwy]))

    print("% features count: " + str(stat_collision_feature_count[hwy]/stat_total_features_count[hwy]))
    print("% nodes count: " + str(stat_collision_node_count[hwy]/stat_total_node_count[hwy]))
    print("% edges cumulative length: " + str(stat_collision_edge_len[hwy]/stat_total_edge_len[hwy]))

    print("----------------")
    print("Post correction")
    print("----------------")
    print("Colliding features count: " + str(stat_corrected_collision_feature_count[hwy]))
    print("Colliding nodes count: " + str(stat_corrected_collision_node_count[hwy]))
    print("Colliding edges cumulative length: " + str(stat_corrected_collision_edge_len[hwy]))

    print("% features count: " + str(stat_corrected_collision_feature_count[hwy]/stat_total_features_count[hwy]))
    print("% nodes count: " + str(stat_corrected_collision_node_count[hwy]/stat_total_node_count[hwy]))
    print("% edges cumulative length: " + str(stat_corrected_collision_edge_len[hwy]/stat_total_edge_len[hwy]))

