# author: Prabhat Kumar Pal
# SMU Id: 47499768

from django.http import HttpResponse
from django.shortcuts import render

import operator
import copy
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
    point_color_list = {}
    returned_details = {}
    terminal_clique_size = 0
    deg_when_deleted = []
    last_order = []

    if request.method == "POST":
        mapped_list = json.loads(request.POST["mapped_list"])
        point_map = json.loads(request.POST["point_map"])
        temp_mapped_list = json.loads(request.POST["mapped_list"])

    for k in temp_mapped_list.keys():
        degree.setdefault(len(temp_mapped_list[k]) - 1, []).append(temp_mapped_list[k][0])

    degree_map = {str(lst[0]): len(lst) - 1 for lst in temp_mapped_list.values()}

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

        deg_when_deleted.append(min_deg)

        last_order.append(str(min_ver))

        remaining_nodes = len(degree_map)
        if remaining_nodes - 1 == c_terminal and terminal_clique_size == 0:
            terminal_clique_size = remaining_nodes

        if len(degree[min_deg]) == 0:
            degree.pop(min_deg)
        degree_map.pop(str(min_ver))

    last_order_copy = last_order[:]

    max_deg_when_deleted = max(deg_when_deleted)

    point_color, color = color_nodes(mapped_list, point_map, last_order_copy)

    for c in point_color.keys():
        point_color_list.setdefault(color.index(point_color[c]), []).append(c)
    color_graph = {k: len(point_color_list[k]) for k in point_color_list.keys()}

    max_color = max(color_graph.iteritems(), key=operator.itemgetter(1))[1]

    end = timeit.default_timer()
    print "Time taken for color generation: " + str(end - start)

    returned_details["point_color"] = json.dumps(point_color)
    returned_details["last_order"] = last_order
    returned_details["point_color_list"] = json.dumps(point_color_list)
    returned_details["color_graph"] = json.dumps(color_graph)
    returned_details["color_list"] = color
    returned_details["max_deg_when_deleted"] = max_deg_when_deleted
    returned_details["terminal_clique_size"] = terminal_clique_size
    returned_details["no_of_colors"] = len(color)
    returned_details["max_color_size"] = max_color

    return HttpResponse(
        json.dumps(returned_details),
        content_type='application/json'
    )


def connected_components(neighbors):
    seen = set()

    def component(n):
        nodes = {n}
        while nodes:
            n = nodes.pop()
            seen.add(n)
            nodes |= neighbors[n] - seen
            yield n
    for node in neighbors:
        if node not in seen:
            yield component(node)


def get_bipartite_backbone(request):
    mapped_list = {}
    point_map = {}
    point_color_list = {}
    returned_details = {}
    color = []
    color_graph = {}
    backbone_list = []
    nodes = 0

    def construct_bipartite(c1, c2):
        bipartite = {str(k): [color[int(top_four_color[c1])]] for k in point_color_list[str(top_four_color[c1])]}
        bipartite.update(
            {str(k): [color[int(top_four_color[c2])]] for k in point_color_list[str(top_four_color[c2])]})

        for key in bipartite:
            for element in mapped_list[str(point_map[key])][1:]:
                if str(mapped_list[str(element)][0]) in bipartite:
                    bipartite[key].append(mapped_list[str(element)][0])

        new_graph = {node: set(str(edge) for edge in edges[1:]) for node, edges in bipartite.items()}
        components = []
        for component in connected_components(new_graph):
            c = set(component)
            components.append({key: bipartite[key] for key in c})

        max_component = max({components.index(comp): len(comp) for comp in components}.iteritems(), key=operator.itemgetter(1))[0]
        return copy.deepcopy(components[max_component])

    if request.method == "POST":
        mapped_list = json.loads(request.POST["mapped_list"])
        point_map = json.loads(request.POST["point_map"])
        point_color_list = json.loads(request.POST["point_color_list"])
        color = json.loads(request.POST["color"])
        color_graph = json.loads(request.POST["color_graph"])
        nodes = request.POST["nodes"]

    top_four_color = sorted(color_graph, key=color_graph.get, reverse=True)[:4]

    for i in range(0, 4):
        for j in range(i + 1, 4):
            backbone_list.append(construct_bipartite(i, j))

    backbone_edge_count = {}
    for bi in range(0, 6):
        s = 0
        for k in backbone_list[bi]:
            s += len(mapped_list[str(point_map[k])]) - 1
        backbone_edge_count[bi] = s

    backbone_index = sorted(backbone_edge_count, key=backbone_edge_count.get, reverse=True)[:2]
    domination = []
    for index in range(0, 2):
        edges = set()
        for key in backbone_list[backbone_index[index]]:
            for edge in mapped_list[str(point_map[key])][1:]:
                edges.add(edge)
                edges.add(point_map[key])

        domination.append(format((len(edges) / float(nodes)) * 100, '.2f'))

    backbone1_edges = sum([len(lst) - 1 for lst in backbone_list[backbone_index[0]].values()]) / 2
    backbone2_edges = sum([len(lst) - 1 for lst in backbone_list[backbone_index[1]].values()]) / 2

    backbone1_vertices = len(backbone_list[backbone_index[0]].keys())
    backbone2_vertices = len(backbone_list[backbone_index[1]].keys())

    returned_details["backbone1"] = json.dumps(backbone_list[backbone_index[0]])
    returned_details["backbone2"] = json.dumps(backbone_list[backbone_index[1]])
    returned_details["backbone1_edges"] = backbone1_edges
    returned_details["backbone2_edges"] = backbone2_edges
    returned_details["backbone1_vertices"] = backbone1_vertices
    returned_details["backbone2_vertices"] = backbone2_vertices
    returned_details["backbone1_coverage"] = domination[0]
    returned_details["backbone2_coverage"] = domination[1]

    return HttpResponse(
        json.dumps(returned_details),
        content_type='application/json'
    )
