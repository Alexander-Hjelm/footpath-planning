import pickle
import statistics
import plot_utils
import geometry_utils

highway_categories = [
        'footpath',
        'residential',
        'secondary',
        'primary'
        ]

statistics_dict = {}

with open('way-collision-statistics', 'rb') as fp:
    statistics_dict = pickle.load(fp)

stat_collision_feature_count = statistics_dict['stat_collision_feature_count']
stat_total_feature_count = statistics_dict['stat_total_feature_count']
stat_collision_node_count = statistics_dict['stat_collision_node_count']
stat_total_node_count = statistics_dict['stat_total_node_count']
stat_collision_edge_len = statistics_dict['stat_collision_edge_len']
stat_total_edge_len = statistics_dict['stat_total_edge_len']
stat_corrected_collision_feature_count = statistics_dict['stat_corrected_collision_feature_count']
stat_corrected_collision_node_count = statistics_dict['stat_corrected_collision_node_count']
stat_corrected_collision_edge_len = statistics_dict['stat_corrected_collision_edge_len']
stat_colliding_features_before_correction = statistics_dict['stat_colliding_features_before_correction']
stat_colliding_features_after_correction = statistics_dict['stat_colliding_features_after_correction']

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

    print("Total features count: " + str(stat_total_feature_count[hwy]))
    print("Total nodes count: " + str(stat_total_node_count[hwy]))
    print("Total edges cumulative length: " + str(stat_total_edge_len[hwy]))

    print("% features count: " + str(stat_collision_feature_count[hwy]/stat_total_feature_count[hwy]))
    print("% nodes count: " + str(stat_collision_node_count[hwy]/stat_total_node_count[hwy]))
    print("% edges cumulative length: " + str(stat_collision_edge_len[hwy]/stat_total_edge_len[hwy]))

    print("----------------")
    print("Post correction")
    print("----------------")
    print("Colliding features count: " + str(stat_corrected_collision_feature_count[hwy]))
    print("Colliding nodes count: " + str(stat_corrected_collision_node_count[hwy]))
    print("Colliding edges cumulative length: " + str(stat_corrected_collision_edge_len[hwy]))

    print("% features count: " + str(stat_corrected_collision_feature_count[hwy]/stat_total_feature_count[hwy]))
    print("% nodes count: " + str(stat_corrected_collision_node_count[hwy]/stat_total_node_count[hwy]))
    print("% edges cumulative length: " + str(stat_corrected_collision_edge_len[hwy]/stat_total_edge_len[hwy]))

print(len(stat_colliding_features_before_correction))
print(len(stat_colliding_features_after_correction))

for id_1 in stat_colliding_features_before_correction.keys():
    for id_2 in stat_colliding_features_before_correction[id_1].keys():
        if id_1 in stat_colliding_features_after_correction.keys():
            if id_2 in stat_colliding_features_after_correction[id_1].keys():
                entry_before = stat_colliding_features_before_correction[id_1][id_2]
                entry_after = stat_colliding_features_after_correction[id_1][id_2]
                feature_1 = entry_before[0]
                feature_2 = entry_before[1]
                polygon_1_before = entry_before[2]
                polygon_2_before = entry_before[3]
                polygon_1_after = entry_after[2]
                polygon_2_after = entry_after[3]

                print("*****")
                print("Polygon 1")
                print(polygon_1_before)
                print(polygon_1_after)
                print("Polygon 2")
                print(polygon_2_before)
                print(polygon_2_after)


                # Plot colliding features
                if 'highway' in feature_2['properties']:
                    plot_utils.plot_edges([polygon_2_before, polygon_2_after, polygon_1_before, polygon_1_after])
                else:
                    plot_utils.plot_polygons_and_paths([polygon_2_before, polygon_2_after], [polygon_1_before, polygon_1_after])
