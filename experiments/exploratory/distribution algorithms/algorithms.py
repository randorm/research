import copy
import json
from typing import Callable

import communities
import networkx as nx
import pandas as pd
from communities.algorithms import louvain_method
import numpy as np
from datastructures import Room


def split_rooms(rooms: list[Room], num_male: int, num_female: int) -> (list[Room], list[Room]):
    dopusk = 10
    exchange_rooms = []
    rooms_female = []
    rooms_male = []
    for room in rooms:
        if room.room_type == 'female':
            rooms_female.append(room)
        elif room.room_type == 'male':
            rooms_male.append(room)
        else:
            exchange_rooms.append(room)
    current_female = np.sum([room.size() for room in rooms_female])
    current_male = np.sum([room.size() for room in rooms_male])

    for room in sorted(exchange_rooms, key=lambda x: x.size(), reverse=True):
        if num_female - current_female > num_male - current_male:
            if current_female + room.size() <= num_female + dopusk:
                rooms_female.append(room)
                current_female += room.size()
        else:
            if current_male + room.size() <= num_male + dopusk:
                rooms_male.append(room)
                current_male += room.size()
    if current_female < num_female or current_male < num_male:
        print(
            f"It was not possible to meet all requirements. "
            f"{num_female - current_female} spaces are needed "
            f"for women and {num_male - current_male} spaces are "
            f"needed for men."
        )
    return rooms_male, rooms_female


def divide_by_rooms(info_df: pd.DataFrame, g: nx.Graph, rooms: list[Room], partition_algo=louvain_method, gender=None):
    """Assigns students to rooms based on room capacities and partitions."""
    if np.sum(room.size() for room in rooms) < len(nx.nodes(g)):
        print("impossible to distribute")
        return
    g_copy = nx.Graph(g)
    if gender is None:
        print(g.nodes)
        nodes_female = info_df[info_df['gender'] == 'female']['id'].index.tolist()
        nodes_male = info_df[info_df['gender'] == 'male']['id'].index.tolist()
        rooms_male, rooms_female = split_rooms(rooms, len(nodes_male), len(nodes_female))
        g_female = nx.Graph(g_copy.subgraph(nodes_female))
        g_male = nx.Graph(g_copy.subgraph(nodes_male))

        divide_by_rooms(info_df, g_female, rooms_female, gender='female')
        divide_by_rooms(info_df, g_male, rooms_male, gender='male')
        return

    count_non_empty = len(rooms)
    happy_students = 0
    while len(g_copy.nodes) != 0:
        list_nodes = g_copy.nodes()
        inverse_map = {i: v for i, v in enumerate(list_nodes)}
        temp_parts = partition_algo(nx.to_numpy_array(g_copy), count_non_empty)[0]
        partition = []
        for cluster in temp_parts:
            partition.append([])
            for item in cluster:
                partition[len(partition) - 1].append(inverse_map[item])

        rooms.sort()
        partition.sort(key=len)

        it1 = len(rooms) - count_non_empty
        it2 = 0
        while it1 != len(rooms) and it2 != len(partition):
            if len(partition[it2]) <= rooms[it1].size():
                for item in partition[it2]:
                    happy_students += 1
                    rooms[it1].student_ids.append(item)
                    g_copy.remove_node(item)
                if rooms[it1].size() == 0:
                    count_non_empty -= 1
                it2 += 1
            else:
                it1 += 1


def divide_by_rooms_randomly(g: nx.Graph, rooms: list[Room]):
    g_copy = copy.deepcopy(g)
    nodes = g_copy.nodes()
    nodes = np.random.permutation(nodes)
    i = 0
    for room in rooms:
        while room.size() != 0:
            room.student_ids.append(nodes[i])
            i += 1


def build_graph(info_df: pd.DataFrame) -> nx.Graph:
    """Builds a NetworkX graph from participant data."""
    g = nx.Graph()
    vertices = info_df['id'].tolist()
    g.add_nodes_from(vertices)
    edges = [(row['id'], subscriber_id) for _, row in info_df.iterrows() for subscriber_id in row['subscriber_ids']]
    g.add_edges_from(edges)
    return g


def build_graph_with_metric(info_df: pd.DataFrame, metric_function: Callable[[pd.DataFrame], np.ndarray]) -> nx.Graph:
    metric_matrix = metric_function(info_df)
    g = nx.Graph()

    num_nodes = len(metric_matrix)
    g.add_nodes_from(range(num_nodes))

    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if metric_matrix[i][j] != np.inf:
                g.add_edge(i, j, weight=metric_matrix[i][j])
            if i != j:
                g.add_edge(j, i, weight=metric_matrix[j][i])
    return g
