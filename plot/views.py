# author: Prabhat Kumar Pal
# SMU Id: 47499768
from django.shortcuts import render

import operator
import timeit
import numpy as np
import json


def calculate_distance(item, comp, mapped_list, number_of_edges, point_map, radius):
    for i in item:
        for j in comp:
            if list(i) != list(j):
                if item == comp and j[0] > i[0]:
                    continue
                dist = (i[0] - j[0]) ** 2 + (i[1] - j[1]) ** 2
                if dist < radius ** 2:
                    number_of_edges['0'] += 1
                    mapped_list.setdefault(str(point_map[str(i)]), [i]).append(point_map[str(j)])
                    mapped_list.setdefault(str(point_map[str(j)]), [j]).append(point_map[str(i)])
            else:
                mapped_list[str(point_map[str(i)])] = mapped_list.setdefault(str(point_map[str(i)]), [i])
        mapped_list[str(point_map[str(i)])] = mapped_list.setdefault(str(point_map[str(i)]), [i])

    return number_of_edges, mapped_list


def get_max_and_min_degree(mapped_list, nodes, deg):
    degree = {str(lst[0]): len(lst)-1 for lst in mapped_list.values()}
    total_degree = sum(degree.values())

    avg_deg_received = float(total_degree) / nodes

    max_deg = max(degree.iteritems(), key=operator.itemgetter(1))[1]
    min_deg = min(degree.iteritems(), key=operator.itemgetter(1))[1]

    max_vertex = [k for k, v in degree.items() if v == max_deg]
    min_vertex = [k for k, v in degree.items() if v == min_deg]

    for i in range(0, len(max_vertex)):
        max_vertex[i] = [float(max_vertex[i].replace('[', '').replace(']', '').split(', ')[0]), float(max_vertex[i].replace('[', '').replace(']', '').split(', ')[1])]
    for i in range(0, len(min_vertex)):
        min_vertex[i] = [float(min_vertex[i].replace('[', '').replace(']', '').split(', ')[0]), float(min_vertex[i].replace('[', '').replace(']', '').split(', ')[1])]

    return min_deg, max_deg, avg_deg_received, max_vertex, min_vertex


def get_point_map(xy, radius, scale):
    cells = {}
    point_map = {}
    x_axis = 0
    col = 0
    count = 0
    no_of_col = np.ceil(scale / radius)
    for i in xy:
        point_map[str(i)] = count
        count += 1

        if not (x_axis <= i[0] < x_axis + radius):
            x_axis += radius
            col += 1
        y_axis = 0
        row = 0
        while y_axis < scale:
            if y_axis <= i[1] < y_axis + radius:
                cells.setdefault(str(int((row * no_of_col) + col)), []).append(i)
                y_axis += radius
                break
            y_axis += radius
            row += 1
    return point_map, no_of_col, cells


def cell_traverse(no_of_col, cells, point_map, radius):
    mapped_list = {}
    number_of_edges = {'0': 0}
    for k in range(0, int(no_of_col ** 2)):
        if str(k) in cells:
            items = cells[str(k)]
            number_of_edges, mapped_list = calculate_distance(items, items, mapped_list, number_of_edges, point_map,
                                                              radius)

            if str(k + 1) in cells and (k + 1) % int(no_of_col) != 0:
                right = cells[str(k + 1)]
                number_of_edges, mapped_list = calculate_distance(items, right, mapped_list, number_of_edges, point_map,
                                                                  radius)

            if 0 < k + int(no_of_col) < int(no_of_col ** 2):
                if str(k + int(no_of_col)) in cells:
                    bottom = cells[str(k + int(no_of_col))]
                    number_of_edges, mapped_list = calculate_distance(items, bottom, mapped_list, number_of_edges,
                                                                      point_map, radius)

                if str(k + int(no_of_col) - 1) in cells and k % int(no_of_col) != 0:
                    bottom_left = cells[str(k + int(no_of_col) - 1)]
                    number_of_edges, mapped_list = calculate_distance(items, bottom_left, mapped_list, number_of_edges,
                                                                      point_map, radius)

                if str(k + int(no_of_col) + 1) in cells and 0 < k + int(no_of_col) + 1 < int(no_of_col ** 2):
                    bottom_right = cells[str(k + int(no_of_col) + 1)]
                    number_of_edges, mapped_list = calculate_distance(items, bottom_right, mapped_list, number_of_edges,
                                                                      point_map, radius)

    return number_of_edges, mapped_list


def square_topology(request, nodes, avg_deg):
    radius = np.sqrt(avg_deg / (nodes * np.pi))

    x = np.random.random(nodes)
    y = np.random.random(nodes)

    xy = []

    for i in range(0, len(x)):
        xy.append([float(format(x[i], '.8f')), float(format(y[i], '.8f'))])

    xy = sorted(xy, key=operator.itemgetter(0))

    point_map, no_of_col, cells = get_point_map(xy, radius, 1)

    number_of_edges, mapped_list = cell_traverse(no_of_col, cells, point_map, radius)

    min_deg, max_deg, avg_deg_received, max_vertex, min_vertex = get_max_and_min_degree(mapped_list, nodes, avg_deg)

    return {'mapped_list': json.dumps(mapped_list), 'avg_deg_received': avg_deg_received, 'max_deg': max_deg,
            'min_deg': min_deg, 'number_of_edges': number_of_edges['0'], 'max_vertex': max_vertex,
            'min_vertex': min_vertex, "radius": radius, "cells": json.dumps(cells), "point_map": json.dumps(point_map),
            "cell_count": no_of_col ** 2}


def circle_topology(request, nodes, avg_deg):
    radius = np.sqrt(float(avg_deg) / nodes)

    theta = np.random.uniform(0.0, 2.0 * np.pi, nodes)
    rad = np.sqrt(np.random.uniform(0.0, 1.0, nodes))
    x = rad * np.cos(theta) + 1
    y = rad * np.sin(theta) + 1

    xy = []
    for i in range(0, len(x)):
        xy.append([float(format(x[i], '.8f')), float(format(y[i], '.8f'))])

    xy = sorted(xy, key=operator.itemgetter(0))

    point_map, no_of_col, cells = get_point_map(xy, radius, 2)

    number_of_edges, mapped_list = cell_traverse(no_of_col, cells, point_map, radius)

    min_deg, max_deg, avg_deg_received, max_vertex, min_vertex = get_max_and_min_degree(mapped_list, nodes, avg_deg)

    return {'mapped_list': json.dumps(mapped_list), 'avg_deg_received': avg_deg_received, 'max_deg': max_deg,
            'min_deg': min_deg, 'number_of_edges': number_of_edges['0'], 'max_vertex': max_vertex,
            'min_vertex': min_vertex, "radius": radius, "cells": json.dumps(cells), "point_map": json.dumps(point_map),
            "cell_count": no_of_col ** 2}


def plot_graph(request):
    topology = "-1"
    nodes = 0
    avg_deg = 0
    returned_details = {}
    plot_option = [-1, -1]
    radius_estimated = 0
    animate = True

    if request.method == "POST":
        topology = request.POST["topology"]
        nodes = request.POST["nodes"]
        avg_deg = request.POST["avg_deg"]
        if "animate[]" in request.POST:
            animate = request.POST["animate[]"]
        temp_plot_option = request.POST.getlist("plot-option[]")
        for i in range(0, len(temp_plot_option)):
            if int(temp_plot_option[i]) == 0:
                plot_option[0] = 0
            if int(temp_plot_option[i]) == 1:
                plot_option[1] = 1

    start = timeit.default_timer()

    if len(topology) > 0:
        if str(topology) == "circle":
            returned_details = circle_topology(request, int(nodes), float(avg_deg))
        elif str(topology) == "square":
            returned_details = square_topology(request, int(nodes), float(avg_deg))

    returned_details["topology"] = str(topology)
    returned_details["plot_option"] = plot_option
    returned_details["avg_deg"] = avg_deg
    returned_details["nodes"] = nodes
    returned_details["topology"] = topology
    returned_details["radius_estimated"] = radius_estimated
    returned_details["animate"] = animate


    stop = timeit.default_timer()
    print("Time taken: " + str(stop - start))

    return render(request, 'plot.html', returned_details)
