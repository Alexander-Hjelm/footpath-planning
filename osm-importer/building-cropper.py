# Processes data with good vertex structure. Removes OSM buildings that interect the edge
# of an OSM query, and the corresponding overlapping buildings in the SLU set
# REQUIREMENTS:
# - Run building-data-formatter-osm.py
# - Run building-data-formatter-slu.py

from geojson import Point, Feature, FeatureCollection, load, dump
import geometry_utils

q_bbox_n = 59.34469860821763
q_bbox_e = 18.066052311607727
q_bbox_s = 59.328128796834925
q_bbox_w = 18.03809503228281
q_p = 0.0015 # Padding for query bbox

q_bbox_n = q_bbox_n - q_p
q_bbox_e = q_bbox_e - q_p
q_bbox_s = q_bbox_s + q_p
q_bbox_w = q_bbox_w + q_p

# read files
with open('raw_data/buildings-osm.geojson', 'r') as f:
    OSM_data = load(f)
with open('raw_data/buildings-slu.geojson', 'r') as f:
    SLU_data = load(f)

OSM_data_out = []
SLU_data_out = []

for feature in SLU_data['features']:
    SLU_data_out.append(feature)

query_polygon = [[q_bbox_w, q_bbox_n],[q_bbox_e, q_bbox_n],[q_bbox_e, q_bbox_s],[q_bbox_w, q_bbox_s],[q_bbox_w, q_bbox_n]]

# Delete any SLU buildings that are outside of the new projected query box
for feature in SLU_data['features']:
    polygon = geometry_utils.extract_polygon_from_feature(feature)
    if geometry_utils.polygon_relative_overlap(polygon, query_polygon) < 0.999:
        SLU_data_out.remove(feature)
        print('Remaining SLU features: ' + str(len(SLU_data_out)))

progress = 0.0
for feature_osm in OSM_data['features']:
    print("Cropping OSM features, progess: " + str(int(100*progress/len(OSM_data['features']))) + '%')
    progress+=1.0

    # Build polygon
    polygon_osm = geometry_utils.extract_polygon_from_feature(feature_osm)
    if geometry_utils.polygon_relative_overlap(polygon_osm, query_polygon) < 0.999:
        for feature_slu in SLU_data['features']:
            if feature_slu in SLU_data_out:
                polygon_slu = geometry_utils.extract_polygon_from_feature(feature_slu)

                relative_overlap = geometry_utils.polygon_relative_overlap(polygon_osm, polygon_slu)
                if relative_overlap > 0.3:
                    SLU_data_out.remove(feature_slu)
                    print('Remaining SLU features: ' + str(len(SLU_data_out)))
    else:
        OSM_data_out.append(feature_osm)

# Delete any buildings that intersect with another building in the same dataset
print("Cropping OSM buildings that intersect with other OSM buildings")
progress = 0.0
candidates_for_removal = []
for feature_osm_1 in OSM_data_out:
    print("Progress: " + str(100*progress/len(OSM_data_out)) + "%")
    progress+=1.0
    # Do not treat multipolygons, since they can have buildings inside of them
    if len(feature_osm_1['geometry']['coordinates']) == 1:
        for feature_osm_2 in OSM_data_out:
            if not feature_osm_1 == feature_osm_2:
                if len(feature_osm_2['geometry']['coordinates']) == 1:
                    polygon_1 = geometry_utils.extract_polygon_from_feature(feature_osm_1)
                    polygon_2 = geometry_utils.extract_polygon_from_feature(feature_osm_2)
                    if geometry_utils.polygon_relative_overlap(polygon_1, polygon_2) > 0.3:
                        if geometry_utils.polygon_area(polygon_1) > geometry_utils.polygon_area(polygon_2):
                            candidates_for_removal.append(feature_osm_2)
                        else:
                            candidates_for_removal.append(feature_osm_1)
print("Removed " + str(len(candidates_for_removal)) + " features from OSM dataset due to self intersection")
for feature in candidates_for_removal:
    if feature in OSM_data_out:
        OSM_data_out.remove(feature)

print("Cropping SLU buildings that intersect with other SLU buildings")
progress = 0.0
candidates_for_removal = []
for feature_slu_1 in SLU_data_out:
    print("Progress: " + str(100*progress/len(SLU_data_out)) + "%")
    progress+=1.0
    # Do not treat multipolygons, since they can have buildings inside of them
    if len(feature_slu_1['geometry']['coordinates']) == 1:
        for feature_slu_2 in SLU_data_out:
            if not feature_slu_1 == feature_slu_2:
                if len(feature_slu_2['geometry']['coordinates']) == 1:
                    polygon_1 = geometry_utils.extract_polygon_from_feature(feature_slu_1)
                    polygon_2 = geometry_utils.extract_polygon_from_feature(feature_slu_2)
                    if geometry_utils.polygon_relative_overlap(polygon_1, polygon_2) > 0.3:
                        if geometry_utils.polygon_area(polygon_1) > geometry_utils.polygon_area(polygon_2):
                            candidates_for_removal.append(feature_slu_2)
                        else:
                            candidates_for_removal.append(feature_slu_1)
print("Removed " + str(len(candidates_for_removal)) + " features from SLU dataset due to self intersection")
for feature in candidates_for_removal:
    if feature in SLU_data_out:
        SLU_data_out.remove(feature) 

# Write all building features to files
with open('raw_data/buildings-osm-cropped.geojson', 'w') as f:
    dump(FeatureCollection(OSM_data_out), f)
with open('raw_data/buildings-slu-cropped.geojson', 'w') as f:
    dump(FeatureCollection(SLU_data_out), f)
