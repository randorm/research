import os

import pandas as pd

from datastructures import Room
from datastructures import create_random_room_list
import algorithms
import visualize
import evaluation

if __name__ == "__main__":
    path_to_data = os.path.join('..', '..', '..', 'data')
    path_to_participants = os.path.join(path_to_data, 'participants.json')
    path_to_info_df = os.path.join(path_to_data, 'info_df.pkl')

    info_df = pd.read_pickle(path_to_info_df)

    G = algorithms.build_graph_with_metric(info_df, evaluation.get_hybrid_similarity_matrix)
    # visualize.plot_graph(G)
    rooms = create_random_room_list(len(G.nodes) + -10)
    algorithms.divide_by_rooms(info_df, G, rooms)
    visualize.print_distribution_statistics(G, rooms)
