import pickle
import statistics
import plot_utils

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

