import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import geometry_utils
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

def plot_edges_and_points(p, e):
    #points = np.array(p)
    #edges = np.array(e)

    #x = points[:,0].flatten()
    #y = points[:,1].flatten()
    #plt.plot(x[edges.T], y[edges.T], 'y-') # Edges
    #plt.plot(x, y, 'ro') # Points

    points = np.array(p)
    edges = np.array(e)

    x = points[:,0].flatten()
    y = points[:,1].flatten()
    plt.plot(x[edges.T], y[edges.T], 'y-') # Edges
    plt.plot(x, y, 'ro') # Points
    plt.show()


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

def plot_scatter(points):
    data = np.array(points)
    x, y = data.T

    # Plot
    plt.scatter(x, y)
    plt.title('Scatter plot')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.show()

def plot_step_function(points):
    plot_step_functions([points])

def plot_step_functions(fns):
    fns_edited = []
    for f in fns:
        fn_edited = []
        for i in range(0, len(f)-1):
            p1 = f[i]
            p2 = f[i+1]
            fn_edited.append(p1)
            fn_edited.append([p2[0]-0.0000001, p1[1]])
        fns_edited.append(fn_edited)
    plot_lines(fns_edited)

def plot_line(points):
    plot_lines([points])

def plot_lines(lines):
    for line in lines:
        data = np.array(line)
        x, y = data.T
        plt.plot(x, y)

    plt.title('Line plot')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.show()

def plot_bar(data_values, bar_width, max_value = None, min_value = None, x_label = None, y_label = None):
    #TODO: Axis labels
    min_val = min(data_values)
    max_val = max(data_values)

    if max_value is not None:
        max_val = max_value
    if min_value is not None:
        min_val = min_value

    counter = min_val + bar_width/2.0
    bars = []
    while counter <= max_val:
        bars.append(counter)
        counter += bar_width
    values = []
    for i in range(0, len(bars)):
        values.append(0)
    for val in data_values:
        for i in range(0, len(bars)-1):
            if val > bars[i] and val < bars[i+1]:
                values[i] += 1
                break

    ax2 = plt.axes()
    if x_label is not None:
        ax2.set_xlabel(x_label)
    if y_label is not None:
        ax2.set_ylabel(y_label)

    plt.bar(bars, values, width=bar_width*0.8)
    plt.show()
