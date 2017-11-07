# author: Prabhat Kumar Pal
# SMU Id: 47499768
from collections import Counter

import xlwt
import xlsxwriter
from django.http import HttpResponse
from django.shortcuts import render

import operator
import copy
import timeit
import numpy as np
import json


def generate_xlsx(color_graph, deg_when_deleted, nodes, avg_deg):
    workbook = xlsxwriter.Workbook("data_" + str(nodes) + "_" + str(avg_deg) + ".xlsx")

    worksheet1 = workbook.add_worksheet()
    # worksheet2 = workbook.add_worksheet()

    worksheet1.write(0, 0, "Nodes")
    worksheet1.write(0, 1, "Time")
    for i in range(len(deg_when_deleted)):
        worksheet1.write(i + 1, 0, i + 1)
        worksheet1.write(i + 1, 1, deg_when_deleted[i][0])
        worksheet1.write(i + 1, 2, deg_when_deleted[i][1])
        worksheet1.write(i + 1, 3, avg_deg)

    # worksheet1.write(0, 0, "Nodes")
    # worksheet1.write(0, 1, "Deg. when deleted")
    # worksheet1.write(0, 2, "Original degree")
    # worksheet1.write(0, 3, "Avg. degree")
    # for i in range(len(deg_when_deleted)):
    #     worksheet1.write(i+1, 0, i+1)
    #     worksheet1.write(i+1, 1, deg_when_deleted[i][0])
    #     worksheet1.write(i+1, 2, deg_when_deleted[i][1])
    #     worksheet1.write(i+1, 3, avg_deg)

    # i = 1
    # worksheet2.write(0, 0, "Color")
    # worksheet2.write(0, 1, "Nodes")
    # for val in color_graph.values():
    #     worksheet2.write(i, 0, i)
    #     worksheet2.write(i, 1, val)
    #     i += 1

    workbook.close()


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


def get_max_and_min_degree(mapped_list, nodes):
    degree = {str(lst[0]): len(lst) - 1 for lst in mapped_list.values()}
    total_degree = sum(degree.values())

    avg_deg_received = float(total_degree) / nodes

    max_deg = max(degree.iteritems(), key=operator.itemgetter(1))[1]
    min_deg = min(degree.iteritems(), key=operator.itemgetter(1))[1]

    max_vertex = [k for k, v in degree.items() if v == max_deg]
    min_vertex = [k for k, v in degree.items() if v == min_deg]

    for i in range(0, len(max_vertex)):
        max_vertex[i] = [float(max_vertex[i].replace('[', '').replace(']', '').split(', ')[0]),
                         float(max_vertex[i].replace('[', '').replace(']', '').split(', ')[1])]
    for i in range(0, len(min_vertex)):
        min_vertex[i] = [float(min_vertex[i].replace('[', '').replace(']', '').split(', ')[0]),
                         float(min_vertex[i].replace('[', '').replace(']', '').split(', ')[1])]

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

    min_deg, max_deg, avg_deg_received, max_vertex, min_vertex = get_max_and_min_degree(mapped_list, nodes)

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

    min_deg, max_deg, avg_deg_received, max_vertex, min_vertex = get_max_and_min_degree(mapped_list, nodes)

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
    returned_details["point_color"] = []

    stop = timeit.default_timer()
    print("Time taken: " + str(stop - start))

    return render(request, 'plot.html', returned_details)


def color_nodes(mapped_list, point_map, last_order):
    point_color = {}
    color = []

    def generate_color():
        r = np.random.random_integers(10, 255)
        g = np.random.random_integers(10, 255)
        b = np.random.random_integers(10, 255)

        return [r, g, b]

    color.append(generate_color())

    while last_order:
        node = last_order.pop()
        color_index = 0
        temp_adj = []
        for adj in mapped_list[str(point_map[str(node)])][1:]:
            if str(mapped_list[str(adj)][0]) in point_color:
                temp_adj.append(color.index(point_color[str(mapped_list[str(adj)][0])]))

        if len(temp_adj) > 0:
            temp_adj = sorted(set(temp_adj))
            for i in temp_adj:
                if color_index == i:
                    color_index += 1

        if color_index > len(color) - 1:
            color.append(generate_color())

        point_color[str(node)] = color[color_index]

    return point_color, color


def smallest_last_order(request):
    degree = {}
    temp_mapped_list = {}
    mapped_list = {}
    point_map = {}
    color_graph = {}
    returned_details = {}
    terminal_clique_size = 0
    deg_when_deleted = []

    if request.method == "POST":
        mapped_list = json.loads(request.POST["mapped_list"])
        point_map = json.loads(request.POST["point_map"])
        temp_mapped_list = json.loads(request.POST["mapped_list"])

    last_order = []
    for k in temp_mapped_list.keys():
        degree.setdefault(len(temp_mapped_list[k]) - 1, []).append(temp_mapped_list[k][0])

    degree_map = {str(lst[0]): len(lst) - 1 for lst in temp_mapped_list.values()}
    degree_map_ref = copy.deepcopy(degree_map)

    start = timeit.default_timer()

    while degree_map:
        min_deg = min(degree.iteritems(), key=operator.itemgetter(0))[0]
        min_ver = degree[min_deg][0]

        c_terminal = 0
        for adj in temp_mapped_list[str(point_map[str(min_ver)])][1:]:
            try:
                adj_point = temp_mapped_list[str(adj)][0]
                deg = degree_map[str(adj_point)]
                degree_map[str(adj_point)] -= 1
                degree.setdefault(deg - 1, []).append(adj_point)
                degree[deg].remove(adj_point)
                c_terminal += 1
                temp_mapped_list[str(adj)].pop(temp_mapped_list[str(adj)].index(point_map[str(min_ver)]))
                if len(degree[deg]) == 0:
                    del degree[deg]
            except KeyError:
                pass
            except ValueError:
                pass

        degree[min_deg].remove(min_ver)

        deg_when_deleted.append([min_deg, degree_map_ref[str(min_ver)]])

        last_order.append(str(min_ver))

        remaining_nodes = len(degree_map)
        if remaining_nodes - 1 == c_terminal and terminal_clique_size == 0:
            terminal_clique_size = remaining_nodes

        if len(degree[min_deg]) == 0:
            degree.pop(min_deg)
        degree_map.pop(str(min_ver))

    last_order_copy = last_order[:]
    point_color, color = color_nodes(mapped_list, point_map, last_order_copy)

    for c in point_color.keys():
        color_graph.setdefault(color.index(point_color[c]), []).append(c)
    color_graph = {k: len(color_graph[k]) for k in color_graph.keys()}

    max_color = max(color_graph.iteritems(), key=operator.itemgetter(1))[1]

    end = timeit.default_timer()
    print "Time taken for color generation: " + str(end - start)

    returned_details["point_color"] = json.dumps(point_color)
    returned_details["last_order"] = last_order
    returned_details["color_graph"] = json.dumps(color_graph)
    returned_details["terminal_clique_size"] = terminal_clique_size
    returned_details["no_of_colors"] = len(color)
    returned_details["max_color_size"] = max_color

    return HttpResponse(
        json.dumps(returned_details),
        content_type='application/json'
    )



