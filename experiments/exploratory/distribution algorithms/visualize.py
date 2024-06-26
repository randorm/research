import networkx as nx
import plotly.graph_objects as go
from matplotlib import pyplot as plt

from datastructures import Room
import evaluation


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


def visualize_assignment(g: nx.Graph, rooms: list[Room]):
    """Visualizes the assignment of students to rooms using Matplotlib."""
    cmap = plt.get_cmap('tab20')
    room_color = [cmap(i % 20) for i in range(len(rooms))]
    node_color = [cmap(0) for _ in range(len(g.nodes))]

    for i, room in enumerate(rooms):
        for student_id in room.student_ids:
            node_color[student_id - 1] = room_color[i]

    pos = nx.spring_layout(g)
    nx.draw(g, pos, node_color=node_color, with_labels=True)
    edges = g.edges()
    nx.draw_networkx_edges(g, pos, edgelist=edges, edge_color='black', arrows=False)
    plt.show()


def print_adjacent(rooms):
    for i, room in enumerate(rooms):
        print(str(i) + ":")
        for item in room.studentsIDs:
            print(item)
        print()


def print_distribution_statistics(g: nx.Graph, rooms: list[Room]):
    print(f"Mean room satisfaction: {100 * evaluation.mean_room_satisfaction(g, rooms)}%")
    print(f"Percentage of edges saved: {100 * evaluation.edges_saved(g, rooms)}%")
