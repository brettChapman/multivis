import networkx as nx
import numpy as np
from networkx.drawing.nx_agraph import pygraphviz_layout
#from networkx.drawing.nx_agraph import spring_layout
import matplotlib.pyplot as plt


def graphviz_plotNetwork(imageFileName, saveImage, g, prog, fontSize, figSize, alpha, addLabels, keepSingletons):

    #size = 3000;

    fig, ax = plt.subplots(figsize=figSize);

    # node_size = np.list(map(int, nx.get_node_attributes(g,'size').values()))
    # node_size = list(nx.get_node_attributes(g,'size').values())
    # node_size = 2000;

    #size = list(range_scale(np.array(list(map(float, df_nodes['node_size'].values))), 500, 3000))

    # node_size = list(map(float, df_nodes['node_size'].values))
    # nx.draw(g, pos=graphviz_layout(g), labels=dict(zip(g.nodes(), g.nodes())), node_size=2000, font_size=fontSize, node_color=list(nx.get_node_attributes(g,'color').values()), prog='neato', alpha=alpha, with_labels=addLabels)

    if not keepSingletons:
        edges = list(g.edges())
        edgeList = []
        for edge in edges:
            source = edge[0]
            target = edge[1]

            edgeList.append(source)
            edgeList.append(target)

        edgeNodes = np.unique(edgeList)

        singleNodes = list(set(edgeNodes).symmetric_difference(set(list(g.nodes()))))

        for node in singleNodes:
            g.remove_node(node)

    #np.multiply(list(nx.get_node_attributes(g, 'size').values()), node_scale)

    #g = nx.petersen_graph()

    pos = pygraphviz_layout(g, prog=prog)

    #pos = nx.spring_layout(g, iterations=1000, pos=pos)

    #nx.draw_graphviz(g, prog=prog)

    #nx.draw(g, pos=pos)

    nx.draw(g, pos=pos, labels=dict(zip(g.nodes(), list(nx.get_node_attributes(g, 'label').values()))), node_size=list(map(int, list(nx.get_node_attributes(g, 'size').values()))), font_size=fontSize, node_color=list(nx.get_node_attributes(g, 'color').values()), alpha=alpha, with_labels=addLabels)

    if saveImage:
        plt.savefig(imageFileName, format="JPG");

    plt.show()