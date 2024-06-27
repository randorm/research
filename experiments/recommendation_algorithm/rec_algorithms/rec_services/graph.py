from typing import List

import networkx as nx
import pandas as pd


class Graph:
    """
    Graph class that represents the participants and their connections.

    Args:
        :param participants_data: DataFrame with participants data
        :param nan_responses: List of participants with NaN responses
    """

    def __init__(
        self, participants_data: pd.DataFrame, nan_responses: List[int] = None
    ):
        self.participants = participants_data.copy()
        self.nan_responses = nan_responses

        self.graph = self.create_graph()

    def create_graph(self) -> nx.DiGraph:
        """Creates a directed graph with the participants.

        Returns:
            nx.DiGraph: Directed graph with the participants
        """
        graph = nx.DiGraph()

        for index, row in self.participants.iterrows():
            if row["id"] not in self.nan_responses:
                graph.add_node(row["id"], **row.to_dict())
        return graph

    def add_edge(self, source: int, target: int) -> None:
        """Adds an edge between the source and target participants. Also, updates the subscription_ids in the participants data.

        Args:
            :param source: Source participant id
            :param target: Target participant id
        """
        self.graph.add_edge(source, target)
        self.participants["subscription_ids"] = self.participants[
            "subscription_ids"
        ].apply(lambda x: x.append(target) if x == source else x)

    def get_n_neighbors(self, node_id: int, n: int) -> List[int]:
        """Returns the first n neighbors of the node_id.

        Args:
            :param node_id: Node id
            :param n: Number of neighbors to return
        """
        return list(self.graph.neighbors(node_id))[:n]

    def get_neighbors(self, node_id: int) -> List[int]:
        """Returns all neighbors of the node_id.

        Args:
            :param node_id: Node id
        """
        return list(self.graph.neighbors(node_id))

    def is_neighbors(self, source: int, target: int) -> bool:
        """Checks if the source and target participants are neighbors.

        Args:
            :param source: Source participant id
            :param target: Target participant id
        """
        return self.graph.has_edge(source, target)


__all__ = ("Graph",)
