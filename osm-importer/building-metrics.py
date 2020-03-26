# This script reads processed OSM and SLU building data, and finds the metrics specified in the project report
# REQUIREMENTS:
# - Run buildings-convert-to-sweref.py

from geojson import Point, Feature, FeatureCollection, load
import geometry_utils
import plot_utils

OSM_data = {}
SLU_data = {}

# read files
with open('raw_data/buildings-osm-sweref.geojson', 'r') as f:
    OSM_data = load(f)
with open('raw_data/buildings-slu-sweref.geojson', 'r') as f:
    SLU_data = load(f)

print("Finished loading map data")

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
progress = 0.0
for feature_osm in OSM_data['features']:
    # Debug only, limit the wating time
    if progress>10:
        break
    print("Mapping features, progess: " + str(int(100*progress/len(OSM_data['features']))) + '%')
    progress+=1.0

    # Build polygon and match with SLU polygons
    polygon_osm = geometry_utils.extract_polygon_from_feature(feature_osm)
    for feature_slu in SLU_data['features']:
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

# Geometrical distance between the two sets
avg_pos_error_cp = 0.0
counted_points_cp = 0
avg_pos_error_mbr = 0.0
counted_points_mbr = 0
for feature_osm in OSM_data['features']:
    # Footprints to a single OSM footprint
    if feature_osm['id'] in overlapping_buildings_osm_bigger:
        features_slu = overlapping_buildings_osm_bigger[feature_osm['id']]

        # Build polygons
        polygon_osm = geometry_utils.extract_polygon_from_feature(feature_osm)
        polygon_slu = []
        for feature_slu in features_slu:
            polygon_slu.append(geometry_utils.extract_polygon_from_feature(feature_slu))


        # TODO: Find out how Fan et al did for situations where a building is made up out of many small footprints
        # Compute convex hulls
        cv_osm = geometry_utils.convex_hull(polygon_osm)
        cv_slu = geometry_utils.convex_hull(polygon_slu)

        #plot_utils.plot_polygon(polygon_osm)
        #plot_utils.plot_polygons(polygon_slu)

        # Turning funcitons
        tc_osm = geometry_utils.turning_function(cv_osm)
        tc_slu = geometry_utils.turning_function(cv_slu)

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

        edges_on_perimeter_osm = geometry_utils.get_edges_on_rect_perimeter(cv_osm, mbr_osm)
        edges_on_perimeter_slu = geometry_utils.get_edges_on_rect_perimeter(cv_slu, mbr_slu)

        #plot_utils.plot_polygons([points_on_perimeter_osm, mbr_osm])
        #plot_utils.plot_polygons([points_on_perimeter_slu, mbr_slu])

        #print(edges_on_perimeter_osm)
        #print(edges_on_perimeter_slu)

        # While both edge sets are non-emptyh
        while edges_on_perimeter_osm and edges_on_perimeter_slu:
            edge_osm = edges_on_perimeter_osm[0]
            best_edge_slu = None
            min_edge_distance = 99999999999.0
            for edge_slu in edges_on_perimeter_slu:
                edge_distance = geometry_utils.edge_endpoints_distance(edge_osm, edge_slu)
                if edge_distance < min_edge_distance:
                    best_edge_slu = edge_slu
                    min_edge_distance = edge_distance
            if(min_edge_distance < 10.0):   # Cutoff point to remove points that were inducted due to mismatching of edges
                avg_pos_error_mbr += min_edge_distance
                counted_points_mbr += 2
                #print(min_edge_distance)
            edges_on_perimeter_osm.remove(edge_osm)
            edges_on_perimeter_slu.remove(best_edge_slu)

            for i in range(0, len(mbr_osm)):
                p1 = mbr_osm[i]
                best_r = 9999999999.0
                p2_best = None
                for p2 in mbr_slu:
                    r = geometry_utils.point_distance(p1, p2)
                    if r < best_r:
                        p2_best = p2
                        best_r = r
                avg_pos_error_cp += best_r
                counted_points_cp += 1

### OUTPUT ###

print("Results...")

print("Total area, OSM: " + str(total_area_OSM))
print("Total area, SLU: " + str(total_area_SLU))
print("Total area, fraction: " + str(total_area_OSM / total_area_SLU))

avg_pos_error_cp /= counted_points_cp
print("Average position error: " + str(avg_pos_error_cp) + " (Counting Points method, upper threshold)")

avg_pos_error_mbr /= counted_points_mbr
print("Average position error: " + str(avg_pos_error_mbr) + " (MBR method, reasonable)")

#TODO: Read through Fan et al, make a list of metrics that we will obtain
