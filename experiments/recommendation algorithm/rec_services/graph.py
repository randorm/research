from typing import List

import networkx as nx
import pandas as pd


class Graph:

    def __init__(self, participants_data: pd.DataFrame):
        self.participants = participants_data.copy()
        self.graph = self.create_graph()

    def create_graph(self) -> nx.DiGraph:
        graph = nx.DiGraph()

        for index, row in self.participants.iterrows():
            graph.add_node(row["id"], **row.to_dict())
        return graph

    def add_edge(self, source: int, target: int) -> None:
        self.graph.add_edge(source, target)
        # self.participants['subscription_ids'] = self.participants['subscription_ids'].apply(
        #     lambda x: x.append(target) if x == source else x)

    def remove_edge(self, source: int, target: int) -> None:
        self.graph.remove_edge(source, target)

    def get_n_neighbors(self, node_id: int, n: int) -> List[int]:
        return list(self.graph.neighbors(node_id))[:n]

    def get_neighbors(self, node_id: int) -> List[int]:
        return list(self.graph.neighbors(node_id))

    def is_neighbors(self, source: int, target: int) -> bool:
        return self.graph.has_edge(source, target)
