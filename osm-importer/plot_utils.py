import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import geometry_utils
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

def plot_polygons(polygons):
    fig, ax = plt.subplots()
    ax.set_xlim(0)
    patches = []

    min_x = 999999999999.0
    min_y = 999999999999.0
    max_x = -999999999999.0
    max_y = -999999999999.0

    for p in polygons:
        patches.append(Polygon(p, True))

        minmax_coords = geometry_utils.minmax_points_of_polygon(p)
        if minmax_coords[0][1] > max_y:
            max_y = minmax_coords[0][1]
        if minmax_coords[1][0] > max_x:
            max_x = minmax_coords[1][0]
        if minmax_coords[2][1] < min_y:
            min_y = minmax_coords[2][1]
        if minmax_coords[3][0] < min_x:
            min_x = minmax_coords[3][0]


    p = PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=0.4)

    colors = 100*np.random.rand(len(patches))
    p.set_array(np.array(colors))

    ax.add_collection(p)

    # Set zoom limits
    r_x = max_x-min_x
    r_y = max_y-min_y
    if r_x > r_y:
        r = r_x-r_y
        min_y -= r/2
        max_y += r/2
    else:
        r = r_y-r_x
        min_x -= r/2
        max_x += r/2

    plt.axis([min_x,max_x,min_y,max_y])
    plt.show()

def plot_polygon(polygon):
    plot_polygons([polygon])
