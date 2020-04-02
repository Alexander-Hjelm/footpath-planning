# This script reads processed OSM and SLU building data, and finds the metrics specified in the project report
# REQUIREMENTS:
# - Run buildings-convert-to-sweref.py

from geojson import Point, Feature, FeatureCollection, load
from geometry_hashtable import GeometryHashtable
import geometry_utils
import plot_utils
import statistics
import sys
import pickle

"""
### Turning function + shape similarity test ###
p1 = [[0.0,0.0],[3.0,0.0],[3.0,3.0],[0.0,3.0]]
p2 = [[0.0,0.0],[4.0,0.0],[4.0,3.0],[0.0,3.0]]
tc_1, tc_2 = geometry_utils.turning_function_2(p1, p2)
print(tc_1)
print(tc_2)
area = geometry_utils.step_functions_area_between(tc_1, tc_2)
d_p1_p2 = geometry_utils.shape_dissimilarity(p1, p2)
sn_p1_p2 = geometry_utils.normalized_shape_dissimilarity(p1, p2)
print("Area: " + str(area))
print("d: " + str(d_p1_p2))
print("Sn: " + str(sn_p1_p2))
plot_utils.plot_step_functions([tc_1, tc_2])
sys.exit()
"""

OSM_data = {}
SLU_data = {}

# read files
with open('raw_data/buildings-osm-sweref.geojson', 'r') as f:
    OSM_data = load(f)
with open('raw_data/buildings-slu-sweref.geojson', 'r') as f:
    SLU_data = load(f)

print("Finished loading map data")

# Build polygon hashtables
print("Building hash tables...")
hashtable_slu = GeometryHashtable("building-hashtable-slu", 230)
hashtable_slu.create_from_features_list(SLU_data['features'])
print("Hash tables complete!")

# Metric: total building area
total_area_OSM = 0.0
total_area_SLU = 0.0
for feature in OSM_data['features']:
    total_area_OSM += geometry_utils.add_areas_recursively(feature['geometry']['coordinates'])
for feature in SLU_data['features']:
    total_area_SLU += geometry_utils.add_areas_recursively(feature['geometry']['coordinates'])

# Feature mapping
overlapping_buildings_osm_bigger = {}
overlapping_buildings_slu_bigger = {}
one_to_one_matches_count = 0
one_to_many_matches_count = 0
total_matches_count = 0

progress = 0.0
for feature_osm in OSM_data['features']:
    # Debug only, limit the wating time
    if progress>10:
        break
    print("Mapping features, progess: " + str(int(100*progress/len(OSM_data['features']))) + '%')
    progress+=1.0

    # Build polygon and match with SLU polygons
    polygon_osm = geometry_utils.extract_polygon_from_feature(feature_osm)

    for feature_slu in hashtable_slu.get_collision_canditates(feature_osm):
        polygon_slu = geometry_utils.extract_polygon_from_feature(feature_slu)

        relative_overlap = geometry_utils.polygon_relative_overlap(polygon_osm, polygon_slu)
        if relative_overlap > 0.3:
            if geometry_utils.polygon_area(polygon_slu) > geometry_utils.polygon_area(polygon_osm):
                if not feature_slu['id'] in overlapping_buildings_slu_bigger.keys():
                    overlapping_buildings_slu_bigger[feature_slu['id']] = []
                overlapping_buildings_slu_bigger[feature_slu['id']].append(feature_osm)
            else:
                if not feature_osm['id'] in overlapping_buildings_osm_bigger.keys():
                    overlapping_buildings_osm_bigger[feature_osm['id']] = []
                overlapping_buildings_osm_bigger[feature_osm['id']].append(feature_slu)

    if feature_osm['id'] in overlapping_buildings_osm_bigger.keys():
        if len(overlapping_buildings_osm_bigger[feature_osm['id']]) == 1:
            one_to_one_matches_count += 1
        elif len(overlapping_buildings_osm_bigger[feature_osm['id']]) > 1:
            one_to_many_matches_count += 1
    total_matches_count += 1

for id_slu in overlapping_buildings_slu_bigger.keys():
    if len(overlapping_buildings_slu_bigger[id_slu]) == 1:
        one_to_one_matches_count += 1
    elif len(overlapping_buildings_slu_bigger[id_slu]) > 1:
        one_to_many_matches_count += 1

# Delete too similar points for each polygon in the data sets
for feature_osm in OSM_data['features']:
    polygon = geometry_utils.extract_polygon_from_feature(feature_osm)
    geometry_utils.prune_polygon(polygon)
for feature_slu in SLU_data['features']:
    polygon = geometry_utils.extract_polygon_from_feature(feature_slu)
    geometry_utils.prune_polygon(polygon)

# Geometrical distance between the two sets
counted_data_points_mbr = []
shape_dissimilarity_data = []
for feature_osm in OSM_data['features']:
    # Footprints to a single OSM footprint
    if feature_osm['id'] in overlapping_buildings_osm_bigger:
        features_slu = overlapping_buildings_osm_bigger[feature_osm['id']]

        # Build polygons
        polygon_osm = geometry_utils.extract_polygon_from_feature(feature_osm)
        polygon_slu = []
        for feature_slu in features_slu:
            polygon_slu.append(geometry_utils.extract_polygon_from_feature(feature_slu))

        # Compute convex hulls
        cv_osm = geometry_utils.convex_hull(polygon_osm)
        cv_slu = geometry_utils.convex_hull(polygon_slu)

        #plot_utils.plot_polygon(polygon_osm)
        #plot_utils.plot_polygons(polygon_slu)

        # Normalized shape dissimilarities, only if there is a 1:1 match
        if len(polygon_slu) == 1:
            # Only buildings with a 1:1 semantic relationship are involved in the measurement of of positional and shape accuracy. Should we do this too?
            shape_dissimilarity_normalized = geometry_utils.normalized_shape_dissimilarity(polygon_osm, polygon_slu[0])
            shape_dissimilarity_data.append(shape_dissimilarity_normalized)
            #print("SDN: " + str(shape_dissimilarity_normalized))

            # Turning funcitons
            #tc_osm, tc_slu = geometry_utils.turning_function_2(polygon_osm, polygon_slu[0])
            #plot_utils.plot_step_functions([tc_osm, tc_slu])
            #plot_utils.plot_polygons([polygon_slu[0], polygon_osm])

            #print("Shape dissimilarity:" + str(shape_dissimilarity_normalized))

        #plot_utils.plot_polygons([cv_osm, polygon_osm])
        #plot_utils.plot_polygons([cv_slu] + polygon_slu)
        #plot_utils.plot_polygons([cv_slu, cv_osm])

        # Remove last points to prepare for Douglas-Peucker
        cv_osm.pop(-1)
        cv_slu.pop(-1)

        # Douglas Peucker-reduced polygon, 5m tolerance for now
        # TODO: Adjust tolerance
        cv_osm_dp = geometry_utils.douglas_peucker(cv_osm, 5)
        cv_slu_dp = geometry_utils.douglas_peucker(cv_slu, 5)

        #plot_utils.plot_polygons([cv_osm, cv_osm_dp])
        #plot_utils.plot_polygons([cv_slu, cv_slu_dp])
        #plot_utils.plot_polygons([cv_osm_dp, cv_slu_dp])

        mbr_osm = geometry_utils.oriented_mbr(cv_osm)
        mbr_slu = geometry_utils.oriented_mbr(cv_slu)

        #plot_utils.plot_polygons([polygon_osm, mbr_osm])
        #plot_utils.plot_polygons([polygon_slu, mbr_slu])

        # Pass both polygons at the same time to the matching function, to pick similar starting points (And c-wise/cc-wise orientation?)
        points_on_perimeter_osm, points_on_perimeter_slu = geometry_utils.get_points_on_rect_perimeter_2(cv_osm_dp, cv_slu_dp)

        #plot_utils.plot_polygons([points_on_perimeter_osm, mbr_osm])
        #plot_utils.plot_polygons([points_on_perimeter_slu, mbr_slu])

        #print(edges_on_perimeter_osm)
        #print(edges_on_perimeter_slu)

        # Calculate average positional offset
        # Position accuracy per building by taking the average of the distance between the corresponding points
        avg_point_distance = 0.0
        counted_points = 0
        # While both edge sets are non-empty
        #print("CH, OSM: " + str(cv_osm))
        #print("CH, SLU: " + str(cv_slu))
        #print("EDGES, OSM: " + str(edges_on_perimeter_osm))
        #print("EDGES, SLU: " + str(edges_on_perimeter_slu))

        #print(points_on_perimeter_osm)
        for i in range(0, 4):
            while points_on_perimeter_osm[i] and points_on_perimeter_slu[i]:
                # Find the current two closest points
                closest_1, closest_2, closest_index_1, closest_index_2 = geometry_utils.closest_points_between_polygons(points_on_perimeter_osm[i], points_on_perimeter_slu[i])

                min_edge_distance = geometry_utils.point_distance(closest_1, closest_2)
                if(min_edge_distance < 10.0):   # Cutoff point to remove points that were inducted due to mismatching of edges
                    avg_point_distance += min_edge_distance
                    counted_points += 1
                #else:
                    #print(min_edge_distance)
                #if(min_edge_distance > 20):
                #    print("Closest point, OSM: " + str(closest_1))
                #    print("Closest point, SLU: " + str(closest_2))
                #    plot_utils.plot_polygons([cv_osm, cv_slu])
                points_on_perimeter_osm[i].remove(closest_1)
                points_on_perimeter_slu[i].remove(closest_2)

        if counted_points > 0:
            counted_data_points_mbr.append(avg_point_distance/counted_points)

### OUTPUT ###

# Write all datapoints to file for later processing
with open('metric-data-pos-acc', 'wb') as fp:
    pickle.dump(counted_data_points_mbr, fp)

with open('metric-data-shape-diss-norm', 'wb') as fp:
    pickle.dump(shape_dissimilarity_data, fp)

print("Results...")

print("#Buildings, OSM: " + str(len(OSM_data['features'])))
print("#Buildings, SLU: " + str(len(SLU_data['features'])))

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


#TODO: Fix hashing so that results are identical

#TODO: Report outline + add space for the metrics and images (think about what metrics and images to include)
#TODO: Pictures for the report
#TODO: Crunch metrics for the report (Remember to remove cutoff point)
