import copy
import json
import plotly.graph_objects as go
import communities.algorithms
import networkx as nx
from matplotlib import pyplot as plt
import numpy as np


class Room:
    def __init__(self, label, capacity, room_type):
        self.label = label
        self.capacity = capacity
        self.room_type = room_type
        self.studentsIDs = []

    def __init__(self):
        self.label = 'noLabel'
        self.capacity = 4  # random.randint(1, 6)
        self.room_type = 'undefined'
        self.studentsIDs = []

    def __str__(self):
        return f"Room Label: {self.label}, Capacity: {self.capacity}, Type: {self.room_type}"

    def size(self):
        return self.capacity - len(self.studentsIDs)

    def __lt__(self, other):
        if not isinstance(other, Room):
            raise ValueError("Can only compare with another Room object.")
        return self.size() < other.size()


def plot_graph(g: nx.Graph):
    pos = nx.spring_layout(g)
    edge_x = []
    edge_y = []
    for edge in g.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1])
        edge_y.extend([y0, y1])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in g.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_adjacency = []
    node_text = []
    for node, adjacency in enumerate(g.adjacency()):
        node_adjacency.append(len(adjacency[1]))
        node_text.append(f'# of connections: {len(adjacency[1])}')

    node_trace.marker.color = node_adjacency
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>Subscribers graph',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    fig.show()


def divide_by_rooms_randomly(g: nx.Graph, rooms: list[Room]):
    g_copy = copy.deepcopy(g)
    nodes = g_copy.nodes()
    nodes = np.random.permutation(nodes)
    i = 0
    for room in rooms:
        while room.size() != 0:
            room.studentsIDs.append(nodes[i])
            i += 1


def divide_by_rooms(g: nx.Graph, rooms: list[Room], partition_algo=communities.algorithms.louvain_method):
    """Assigns students to rooms based on room capacities and partitions."""
    g_copy = copy.deepcopy(g)

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
                    rooms[it1].studentsIDs.append(item)
                    g_copy.remove_node(item)
                if rooms[it1].size() == 0:
                    count_non_empty -= 1
                it2 += 1
            else:
                it1 += 1


def visualize_assignment(g: nx.Graph, rooms: list[Room]):
    """Visualizes the assignment of students to rooms using Matplotlib."""
    cmap = plt.get_cmap('tab20')
    room_color = [cmap(i % 20) for i in range(len(rooms))]
    node_color = [cmap(0) for _ in range(len(g.nodes))]

    for i, room in enumerate(rooms):
        for student_id in room.studentsIDs:
            node_color[student_id - 1] = room_color[i]

    pos = nx.spring_layout(g)
    nx.draw(g, pos, node_color=node_color, with_labels=True)
    edges = g.edges()
    nx.draw_networkx_edges(g, pos, edgelist=edges, edge_color='black', arrows=False)
    plt.show()


def build_graph(data):
    """Builds a NetworkX graph from participant data."""
    g = nx.Graph()
    vertices = [item['id'] for item in data]
    g.add_nodes_from(vertices)
    edges = [(item1['id'], adjacent) for item1 in data for adjacent in item1['subscriber_ids']]
    g.add_edges_from(edges)
    return g


def print_adjacent(rooms):
    for i, room in enumerate(rooms):
        print(str(i) + ":")
        for item in room.studentsIDs:
            print(item)
        print()


with open('./datagraph/participants.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

G = build_graph(data)

rooms = [Room() for _ in range(55)]
divide_by_rooms(G, rooms)
number_connections = [len(G.subgraph(room.studentsIDs).edges) for room in rooms]

print(f"Mean room satisfaction: {50 * np.mean(number_connections) / 3}%")
print(f"Percentage of edges saved: {100 * np.sum(number_connections) / len(G.edges)}%")
