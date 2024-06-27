import os

import networkx as nx
import numpy as np
from scipy import spatial
import pandas as pd

from datastructures import Room
from algorithms import build_graph


def connections_inside_room(g: nx.Graph, rooms: list[Room]):
    number_connections = [len(g.subgraph(room.student_ids).edges) for room in rooms]
    return number_connections


def mean_room_satisfaction(g: nx.Graph, rooms: list[Room]):
    number_connections = connections_inside_room(g, rooms)
    room_satisfactions = []
    for connection, room in zip(number_connections, rooms):
        occupied_spaces = room.capacity - room.size()
        max_num_connections = occupied_spaces * (occupied_spaces - 1)
        if max_num_connections == 0:
            room_satisfactions.append(1)
        else:
            room_satisfactions.append(connection / max_num_connections)
    return np.mean(room_satisfactions)


def get_content_similarity_matrix(df: pd.DataFrame) -> np.ndarray:
    """
    Optimized function to calculate the content similarity matrix for all pairs of users.

    :param df: DataFrame containing user data.
    :return: A matrix where element [i][j] represents the similarity between user i and user j.
    """
    unique_ids = df['id'].unique()
    n_users = len(unique_ids)
    similarity_matrix = np.zeros((n_users, n_users))

    vectors = df.set_index('id')['option'].to_dict()

    for i, id_i in enumerate(unique_ids):
        for j, id_j in enumerate(unique_ids[i+1:], start=i+1):
            vec_i = vectors[id_i]
            vec_j = vectors[id_j]

            max_len = max(len(vec_i), len(vec_j))
            vec_i = np.pad(vec_i, (0, max_len - len(vec_i)), 'constant')
            vec_j = np.pad(vec_j, (0, max_len - len(vec_j)), 'constant')

            similarity = 1 - spatial.distance.cosine(vec_i, vec_j)
            similarity_matrix[i, j] = similarity
            similarity_matrix[j, i] = similarity

    return similarity_matrix


def get_content_similarity(df: pd.DataFrame, user_id1: int, user_id2: int):
    """Calculates the cosine similarity between two users' content."""
    vec1 = df[df['id'] == user_id1]['option'].iloc[0]
    vec2 = df[df['id'] == user_id2]['option'].iloc[0]

    # Pad the shorter vector with zeros
    max_len = max(len(vec1), len(vec2))
    vec1 = np.pad(vec1, (0, max_len - len(vec1)), 'constant')
    vec2 = np.pad(vec2, (0, max_len - len(vec2)), 'constant')

    result = 1 - spatial.distance.cosine(vec1, vec2)
    return result


def get_graph_similarity_matrix(df: pd.DataFrame) -> np.ndarray:
    """
    Calculates the distance matrix for all pairs of users in the graph.

    :param df: DataFrame containing user data.
    :return: A matrix where element [i][j] represents the shortest distance between user i and user j.
    """
    naive_graph = build_graph(df)
    spl = dict(nx.all_pairs_shortest_path_length(naive_graph))
    unique_ids = df['id'].unique()
    n_unique = len(unique_ids)
    distance_matrix = np.full((n_unique, n_unique), 0)

    for i, id_i in enumerate(unique_ids):
        for j, id_j in enumerate(unique_ids[i + 1:], start=i + 1):
            similarity = 0
            if id_j in spl[id_i].keys():
                similarity += spl[id_i][id_j]
            if id_i in spl[id_j].keys():
                similarity += spl[id_j][id_i]
            distance_matrix[i, j] = 1 / similarity if similarity != 0 else 0
    return distance_matrix


def get_graph_similarity(df: pd.DataFrame, user_id1: int, user_id2: int):
    naive_graph = build_graph(df)
    spl = dict(nx.all_pairs_shortest_path_length(naive_graph))
    similarity = 0
    if user_id2 in spl[user_id1].keys():
        similarity += spl[user_id1][user_id2]
    if user_id1 in spl[user_id2].keys():
        similarity += spl[user_id2][user_id1]
    return 1 / similarity if similarity != 0 else 0


def get_hybrid_similarity_matrix(df: pd.DataFrame) -> np.ndarray:
    return get_graph_similarity_matrix(df) * 0.7 + get_content_similarity_matrix(df) * 0.3


def hybrid_similarity_score(df: pd.DataFrame, user_id1: int, user_id2: int):
    similarity = 0
    similarity += get_content_similarity(df, user_id1, user_id2) * 0.3
    similarity += get_graph_similarity(df, user_id1, user_id2) * 0.7
    return similarity


def edges_saved(g: nx.Graph, rooms: list[Room]):
    number_connections = connections_inside_room(g, rooms)
    return np.sum(number_connections) / len(g.edges)


if __name__ == "__main__":
    path_to_data = os.path.join('..', '..', '..', 'data')
    path_to_info_df = os.path.join(path_to_data, 'info_df.pkl')
    info_df = pd.read_pickle(path_to_info_df)
    print(get_graph_similarity_matrix(info_df))
