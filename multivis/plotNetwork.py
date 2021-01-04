import sys
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import copy
from .utils import *
import warnings

class plotNetwork:
    """Class for plotNetwork to produce a static spring-embedded network.

        Initial_Parameters
        ----------
        g : NetworkX graph.

        Methods
        -------
        set_params : Set parameters -
            imageFileName: The image file name to save to (default: 'networkPlot.jpg')
            edgeLabels: Setting to 'True' labels all edges with the similarity score (default: True)
            saveImage: Setting to 'True' will save the image to file (default: True)
            layout: Set the NetworkX layout type ('circular', 'kamada_kawai', 'random', 'spring', 'spectral') (default: 'spring')
            dpi: The number of Dots Per Inch (DPI) for the image (default: 200)
            figSize: The figure size as a tuple (width,height) (default: (30,20))
            node_cmap: The CMAP colour palette to use for nodes (default: 'brg')
            colorScale: The scale to use for colouring the nodes ("linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume", "ordinal") (default: 'linear')
            node_color_column: The Peak Table column to use for node colours (default: None sets to black)
            sizeScale: The node size scale to apply ("linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume", "ordinal") (default: 'reverse_linear')
            size_range: The node size scale range to apply. Tuple of length 2. Minimum size to maximum size (default: (150,2000))
            sizing_column: The node sizing column to use (default: sizes all nodes to 1)
            alpha:  Node opacity value (default: 0.5)
            nodeLabels: Setting to 'True' will label the nodes (default: True)
            fontSize: The font size set for each node (default: 15)
            keepSingletons: Setting to 'True' will keep any single nodes not connected by edges in the NetworkX graph) (default: True)
            column: Column from Peak Table to filter on (default: no filtering)
            threshold: Value to filter on (default: no filtering)
            operator: The comparison operator to use when filtering (default: '>')
            sign: The sign of the score to filter on ('pos', 'neg' or 'both') (default: 'pos')

        build : Generates and displays the NetworkX graph.
    """

    def __init__(self, g):

        self.__g = self.__checkData(copy.deepcopy(g))

        self.set_params()

    def set_params(self, imageFileName='networkPlot.jpg', edgeLabels=True, saveImage=True, layout='spring', dpi=200, figSize=(30,20), node_cmap='brg', colorScale='linear', node_color_column='none', sizeScale='reverse_linear', size_range=(150,2000), sizing_column='none', alpha=0.5, nodeLabels=True, fontSize=15, keepSingletons=True, column='none', threshold=0.01, operator='>', sign='pos'):

        imageFileName, edgeLabels, saveImage, layout, dpi, figSize, node_cmap, colorScale, node_color_column, sizeScale, size_range, sizing_column, alpha, nodeLabels, fontSize, keepSingletons, column, threshold, operator, sign = self.__paramCheck(imageFileName, edgeLabels, saveImage, layout, dpi, figSize, node_cmap, colorScale, node_color_column, sizeScale, size_range, sizing_column, alpha, nodeLabels, fontSize, keepSingletons, column, threshold, operator, sign)

        self.__imageFileName = imageFileName;
        self.__edgeLabels = edgeLabels;
        self.__saveImage = saveImage;
        self.__layout = layout;
        self.__dpi = dpi
        self.__figSize = figSize;
        self.__node_cmap = node_cmap;
        self.__colorScale = colorScale;
        self.__node_color_column = node_color_column;
        self.__sizeScale = sizeScale;
        self.__size_range = size_range;
        self.__sizing_column = sizing_column;
        self.__alpha = alpha
        self.__nodeLabels = nodeLabels
        self.__fontSize = fontSize;
        self.__keepSingletons = keepSingletons;
        self.__filter_column = column;
        self.__filter_threshold = threshold;
        self.__operator = operator;
        self.__sign = sign;

    def build(self):

        warnings.filterwarnings("ignore")

        g = self.__g

        plt.subplots(figsize=self.__figSize);

        edgeList = []
        for idx, (source, target) in enumerate(g.edges()):

            weight = g.edges[source, target]['weight']

            if self.__sign == "pos":
                if weight < 0:
                    edgeList.append((source, target))
            elif self.__sign == "neg":
                if weight >= 0:
                    edgeList.append((source, target))

        g.remove_edges_from(edgeList)

        if self.__filter_column != 'none':
            nodeList = []
            for idx, node in enumerate(g.nodes()):

                value = float(g.node[node][self.__filter_column])
                if np.isnan(value):
                    value = 0;

                if self.__operator == ">":
                    if value > float(self.__filter_threshold):
                        nodeList.append(node)
                elif self.__operator == "<":
                    if value < float(self.__filter_threshold):
                        nodeList.append(node)
                elif self.__operator == "<=":
                    if value <= float(self.__filter_threshold):
                        nodeList.append(node)
                elif self.__operator == ">=":
                    if value >= float(self.__filter_threshold):
                        nodeList.append(node)

            for node in nodeList:
                g.remove_node(node)

        if not self.__keepSingletons:
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

        if not g.nodes():
            print("Error: All nodes have been removed. Please change the filter parameters.")
            sys.exit()

        if self.__sizing_column == 'none':
            size_attr = np.ones(len(g.nodes()))
        else:
            size_attr = np.array(list(nx.get_node_attributes(g, str(self.__sizing_column)).values()))

            if self.__sizeScale != "ordinal":
                df_size_attr = pd.Series(size_attr, dtype=np.float);
                size_attr = np.array(list(df_size_attr.fillna(0).values))

        node_size = scaleData(size_attr, self.__sizeScale, self.__size_range[0], self.__size_range[1])

        if self.__layout == "circular":
            pos = nx.circular_layout(g)
        elif self.__layout == "kamada_kawai":
            pos = nx.kamada_kawai_layout(g)
        elif self.__layout == "random":
            pos = nx.random_layout(g)
        elif self.__layout == "spring":
            pos = nx.spring_layout(g)
        elif self.__layout == "spectral":
            pos = nx.spectral_layout(g)

        node_color = []
        nodeCmap = plt.cm.get_cmap(self.__node_cmap)   # Sets the color palette for the nodes

        if self.__node_color_column == 'none':
            node_color = "#000000"
        else:
            colorsHEX = []

            node_color_values = np.array(list(nx.get_node_attributes(g, str(self.__node_color_column)).values()))

            try:
                float(node_color_values[0])

                node_color_values = np.array([float(i) for i in node_color_values])

                colorsRGB = self.__get_colors(node_color_values, nodeCmap)[:, :3]

                for rgb in colorsRGB:
                    colorsHEX.append(matplotlib.colors.rgb2hex(rgb))

                node_color = colorsHEX
            except ValueError:
                if matplotlib.colors.is_color_like(node_color_values[0]):
                    node_color = node_color_values
                else:
                    if self.__colorScale != "ordinal":
                        print("Error: Node colour column is not valid. While colorScale is not ordinal, choose a column containing colour values, floats or integer values.")
                        sys.exit()
                    else:
                        colorsRGB = self.__get_colors(node_color_values, nodeCmap)[:, :3]

                        for rgb in colorsRGB:
                            colorsHEX.append(matplotlib.colors.rgb2hex(rgb))

                        node_color = colorsHEX

        nx.draw(g, pos=pos, labels=dict(zip(g.nodes(), list(nx.get_node_attributes(g, 'Label').values()))), node_size=node_size, font_size=self.__fontSize, node_color=node_color, alpha=self.__alpha, with_labels=self.__nodeLabels)

        if self.__edgeLabels:

            edge_labels = dict({})
            for idx, (source, target) in enumerate(g.edges()):
                weight = g.edges[source, target]['weight']

                edge_labels.update({(source, target): float("{0:.2f}".format(weight))})

            nx.draw_networkx_edge_labels(g, pos=pos, edge_labels=edge_labels)

        if self.__saveImage:
            plt.savefig(self.__imageFileName, dpi=self.__dpi)

        plt.show()

    def __checkData(self, g):

        if not isinstance(g, nx.classes.graph.Graph):
            print("Error: A NetworkX graph was not entered. Please check your data.")
            sys.exit()

        return g

    def __paramCheck(self, imageFileName, edgeLabels, saveImage, layout, dpi, figSize, node_cmap, colorScale, node_color_column, sizeScale, size_range, sizing_column, alpha, nodeLabels, fontSize, keepSingletons, filter_column, filter_threshold, operator, sign):

        g = self.__g
        col_list = list(g.nodes[list(g.nodes.keys())[0]].keys()) + ['none']

        if not isinstance(imageFileName, str):
            print("Error: Image file name is not valid. Choose a string value.")
            sys.exit()

        if not type(edgeLabels) == bool:
            print("Error: Edge labels is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not type(saveImage) == bool:
            print("Error: Save image is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if layout not in ["circular", "kamada_kawai", "random", "spring", "spectral"]:
            print("Error: Layout program not valid. Choose either \"circular\", \"kamada_kawai\", \"random\", \"spring\", \"spectral\".")
            sys.exit()

        if not isinstance(dpi, float):
            if not isinstance(dpi, int):
                print("Error: Dpi is not valid. Choose a float or integer value.")
                sys.exit()

        if not isinstance(figSize, tuple):
            print("Error: Figure size is not valid. Choose a tuple of length 2.")
            sys.exit()
        else:
            for length in figSize:
                if not isinstance(length, float):
                    if not isinstance(length, int):
                        print("Error: Figure size items not valid. Choose a float or integer value.")
                        sys.exit()

        if not isinstance(node_cmap, str):
            print("Error: Node CMAP is not valid. Choose a string value.")
            sys.exit()
        else:
            cmap_list = matplotlib.cm.cmap_d.keys()

            if node_cmap not in cmap_list:
                print("Error: Node CMAP is not valid. Choose one of the following: {}.".format(', '.join(cmap_list)))
                sys.exit()

        if colorScale.lower() not in ["linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume", "ordinal"]:
            print("Error: Color scale type not valid. Choose either \"linear\", \"reverse_linear\", \"log\", \"reverse_log\", \"square\", \"reverse_square\", \"area\", \"reverse_area\", \"volume\", \"reverse_volume\", \"ordinal\".")
            sys.exit()

        if node_color_column not in col_list:
            print("Error: Node color column not valid. Choose one of {}.".format(', '.join(col_list)))
            sys.exit()
        else:
            if node_color_column != 'none':
                node_color_values = np.array(list(nx.get_node_attributes(g, str(node_color_column)).values()))

                if colorScale != 'ordinal':
                    try:
                        float(node_color_values[0])
                    except ValueError:
                        if not matplotlib.colors.is_color_like(node_color_values[0]):
                            print("Error: Node colour column is not valid. While colorScale is not ordinal, choose a column containing colour values, floats or integer values.")
                            sys.exit()

        if sizeScale.lower() not in ["linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume", "ordinal"]:
            print("Error: Size scale type not valid. Choose either \"linear\", \"reverse_linear\", \"log\", \"reverse_log\", \"square\", \"reverse_square\", \"area\", \"reverse_area\", \"volume\", \"reverse_volume\", \"ordinal\".")
            sys.exit()

        if not isinstance(size_range, tuple):
            print("Error: Size range is not valid. Choose a tuple of length 2.")
            sys.exit()
        else:
            for size in size_range:
                if not isinstance(size, float):
                    if not isinstance(size, int):
                        print("Error: Size values not valid. Choose a float or integer value.")
                        sys.exit()

        if sizing_column not in col_list:
            print("Error: Sizing column not valid. Choose one of {}.".format(', '.join(col_list)))
            sys.exit()
        else:

            if sizing_column != 'none':
                for idx, node in enumerate(g.nodes()):
                    if sizeScale != 'ordinal':
                        try:
                            float(g.node[node][sizing_column])
                        except ValueError:
                            print("Error: Sizing column contains invalid values. While sizeScale is not ordinal, choose a sizing column containing float or integer values.")
                            sys.exit()

        if not isinstance(alpha, float):
            if not (alpha >= 0 and alpha <= 1):
                print("Error: Alpha value is not valid. Choose a float between 0 and 1.")
                sys.exit()

        if not type(nodeLabels) == bool:
            print("Error: Add labels is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(fontSize, float):
            if not isinstance(fontSize, int):
                print("Error: Font size is not valid. Choose a float or integer value.")
                sys.exit()

        if not type(keepSingletons) == bool:
            print("Error: Keep singletons is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if filter_column not in col_list:
            print("Error: Filter column not valid. Choose one of {}.".format(', '.join(col_list)))
            sys.exit()
        else:

            if filter_column != 'none':
                for idx, node in enumerate(g.nodes()):
                    try:
                        float(g.node[node][filter_column])
                    except ValueError:
                        print("Error: Filter column contains invalid values. Choose a filter column containing float or integer values.")
                        sys.exit()

        if not isinstance(filter_threshold, float):
            if not isinstance(filter_threshold, int):
                print("Error: Filter threshold is not valid. Choose a float or integer value.")
                sys.exit()
            elif filter_threshold == 0:
                print("Error: Filter threshold should not be zero. Choose a value close to zero or above.")
                sys.exit()
        elif filter_threshold == 0.0:
            print("Error: Filter threshold should not be zero. Choose a value close to zero or above.")
            sys.exit()

        if operator not in ["<", ">", "<=", ">="]:
            print("Error: Operator not valid. Choose either \"<\", \">\", \"<=\" or \">=\".")
            sys.exit()

        if sign.lower() not in ["pos", "neg", "both"]:
            print("Error: Sign not valid. Choose either \"pos\", \"neg\", or \"both\".")
            sys.exit()

        return imageFileName, edgeLabels, saveImage, layout, dpi, figSize, node_cmap, colorScale, node_color_column, sizeScale, size_range, sizing_column, alpha, nodeLabels, fontSize, keepSingletons, filter_column, filter_threshold, operator, sign

    def __get_colors(self, x, cmap):

        scaled_colors = scaleData(x, self.__colorScale, 0, 1)

        return cmap(scaled_colors)