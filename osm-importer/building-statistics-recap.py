import pickle
import statistics
import plot_utils

counted_data_points_mbr = []
shape_dissimilarity_data = []

with open('metric-data-pos-acc', 'rb') as fp:
    counted_data_points_mbr = pickle.load(fp)

with open('metric-data-shape-diss-norm', 'rb') as fp:
    shape_dissimilarity_data = pickle.load(fp)

statistics_dict = {}

with open('metric-data-statistics', 'rb') as fp:
    statistics_dict = pickle.load(fp)

building_count_osm = statistics_dict["building_count_osm"]
building_count_slu = statistics_dict["building_count_slu"]

total_area_OSM = statistics_dict["total_area_osm"]
total_area_SLU = statistics_dict["total_area_slu"]
building_count_osm = statistics_dict["building_count_osm"]

total_matches_count = statistics_dict["total_matches_count"]
one_to_one_matches_count = statistics_dict["one_to_one_matches_count"]
one_to_many_matches_count = statistics_dict["one_to_many_matches_count"]

print(statistics_dict)


print("Results...")

print("#Buildings, OSM: " + str(building_count_osm))
print("#Buildings, SLU: " + str(building_count_slu))

print("Total area, OSM: " + str(total_area_OSM))
print("Total area, SLU: " + str(total_area_SLU))
print("Total area, fraction: " + str(total_area_OSM / total_area_SLU))

# Metric: Statistic of the matching result using area overlap (Fan et al, page 9)
print("Number of 1:1 matches: " + str(one_to_one_matches_count))
print("Number of 1:N matches: " + str(one_to_many_matches_count))
print("Number of 1:0 matches: " + str(total_matches_count - one_to_one_matches_count - one_to_many_matches_count))

# Metric: Max, min and std deviation of position offsets (Fan et al, page 12)
print("Average position error: " + str(statistics.mean(counted_data_points_mbr)) + " (MBR method, reasonable)")
print("Position error, max: " + str(max(counted_data_points_mbr)))
print("Position error, min: " + str(min(counted_data_points_mbr)))
print("Position error, stdev: " + str(statistics.stdev(counted_data_points_mbr)))

# Metric: Bar diagram of position offsets (Fan et al, page 12)
plot_utils.plot_bar(counted_data_points_mbr, 1.0)

# Metric: Bar diagram of footprint shape similarity (Fan et al, page 12)
plot_utils.plot_bar(shape_dissimilarity_data, 0.1)
