import sys
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
from .utils import *
import warnings

class plotNetwork:
    """Class for plotNetwork to produce a static spring-embedded network.

        Parameters
        ----------
        g : NetworkX graph.

        Methods
        -------
        set_params : Set parameters - node parameters dictionary(node sizing columnn, node size scale, node size range, alpha opacity value, node labelling flag, font size and keep single nodes flag)
                                    , filter parameters dictionary(filter column, filter threshold, filter operator and sign)
                                    , image filename, label edges flag, save image flag, NetworkX layout type, dpi, figure size.
        run : Generates and displays the NetworkX graph.
    """

    def __init__(self, g):

        self.__g = self.__checkData(copy.deepcopy(g))

        self.set_params()
        self.__set_node_params()
        self.__set_filter_params()

    def set_params(self, node_params={}, filter_params={}, imageFileName='networkPlot.jpg', edgeLabels=True, saveImage=True, layout='spring', dpi=200, figSize=(30,20)):

        if node_params:
            self.__set_node_params(**node_params)

        if filter_params:
            self.__set_filter_params(**filter_params)

        imageFileName, edgeLabels, saveImage, layout, dpi, figSize = self.__paramCheck(imageFileName, edgeLabels, saveImage, layout, dpi, figSize)

        self.__imageFileName = imageFileName;
        self.__edgeLabels = edgeLabels;
        self.__saveImage = saveImage;
        self.__layout = layout;
        self.__dpi = dpi
        self.__figSize = figSize;

    def run(self):

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
            df_size_attr = pd.Series(size_attr, dtype=np.float);
            size_attr = np.array(list(df_size_attr.fillna(0).values))

        size = np.array([x for x in list(range_scale(size_attr, 1, 10))])

        if self.__sizeScale == 'linear':
            node_size = [x for x in list(range_scale(size, self.__size_range[0], self.__size_range[1]))]
        if self.__sizeScale == 'reverse_linear':
            size = np.divide(1, size)
            node_size = [x for x in list(range_scale(size, self.__size_range[0], self.__size_range[1]))]
        elif self.__sizeScale == 'log':
            size = np.log(size)
            node_size = [x for x in list(range_scale(size, self.__size_range[0], sellf.__size_range[1]))]
        elif self.__sizeScale == 'reverse_log':
            size = np.divide(1, size)
            size = np.log(size)
            node_size = [x for x in list(range_scale(size, self.__size_range[0], self.__size_range[1]))]
        elif self.__sizeScale == 'square':
            size = np.square(size)
            node_size = [x for x in list(range_scale(size, self.__size_range[0], self.__size_range[1]))]
        elif self.__sizeScale == 'reverse_square':
            size = np.divide(1, size)
            size = np.square(size)
            node_size = [x for x in list(range_scale(size, self.__size_range[0], self.__size_range[1]))]
        elif self.__sizeScale == 'area':
            size = np.square(size)
            size = [np.multiply(x, np.pi) for x in list(map(float, size))]
            node_size = [round(x) for x in list(map(int, range_scale(size, self.__size_range[0], self.__size_range[1])))]
        elif self.__sizeScale == 'reverse_area':
            size = np.divide(1, size)
            size = np.square(size)
            size = [np.multiply(x, np.pi) for x in list(map(float, size))]
            node_size = [round(x) for x in list(map(int, range_scale(size, self.__size_range[0], self.__size_range[1])))]
        elif self.__sizeScale == 'volume':
            size = [np.power(x, 3) for x in list(map(float, size))]
            size = [np.multiply(x, np.pi) for x in list(map(float, size))]
            size = [np.multiply(x, 4 / 3) for x in list(map(float, size))]
            node_size = [round(x) for x in list(map(int, range_scale(size, self.__size_range[0], self.__size_range[1])))]
        elif self.__sizeScale == 'reverse_volumn':
            size = np.divide(1, size)
            size = [np.power(x, 3) for x in list(map(float, size))]
            size = [np.multiply(x, np.pi) for x in list(map(float, size))]
            size = [np.multiply(x, 4 / 3) for x in list(map(float, size))]
            node_size = [round(x) for x in list(map(int, range_scale(size, self.__size_range[0], self.__size_range[1])))]

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

        nx.draw(g, pos=pos, labels=dict(zip(g.nodes(), list(nx.get_node_attributes(g, 'Label').values()))), node_size=node_size, font_size=self.__fontSize, node_color=list(nx.get_node_attributes(g, 'Color').values()), alpha=self.__alpha, with_labels=self.__nodeLabels)

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
            print("Error: A networkx graph was not entered. Please check your data.")
            sys.exit()

        return g

    def __set_node_params(self, sizing_column='none', sizeScale='reverse_linear', size_range=(150,2000), alpha=0.5, nodeLabels=True, fontSize=15, keepSingletons=True):

        sizing_column, sizeScale, size_range, alpha, nodeLabels, fontSize, keepSingletons = self.__node_paramCheck(sizing_column, sizeScale, size_range, alpha, nodeLabels, fontSize, keepSingletons)

        self.__sizing_column = sizing_column;
        self.__sizeScale = sizeScale;
        self.__size_range = size_range;
        self.__alpha = alpha
        self.__nodeLabels = nodeLabels
        self.__fontSize = fontSize;
        self.__keepSingletons = keepSingletons;

    def __set_filter_params(self, column='none', threshold=0.01, operator='>', sign='both'):

        column, threshold, operator, sign = self.__filter_paramCheck(column, threshold, operator, sign)

        self.__filter_column = column;
        self.__filter_threshold = threshold;
        self.__operator = operator;
        self.__sign = sign;

    def __paramCheck(self, imageFileName, edgeLabels, saveImage, layout, dpi, figSize):

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

        return imageFileName, edgeLabels, saveImage, layout, dpi, figSize

    def __node_paramCheck(self, sizing_column, sizeScale, size_range, alpha, nodeLabels, fontSize, keepSingletons):

        g = self.__g
        col_list = list(g.nodes[list(g.nodes.keys())[0]].keys())[:-2] + ['none']

        if sizing_column not in col_list:
            print("Error: Sizing column not valid. Choose one of {}.".format(', '.join(col_list)))
            sys.exit()
        else:

            if sizing_column != 'none':
                for idx, node in enumerate(g.nodes()):
                    try:
                        float(g.node[node][sizing_column])
                    except ValueError:
                        print("Error: Sizing column contains invalid values. Choose a sizing column containing float or integer values.")
                        sys.exit()

        if sizeScale.lower() not in ["linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume"]:
            print("Error: Size scale type not valid. Choose either \"linear\", \"reverse_linear\", \"log\", \"reverse_log\", \"square\", \"reverse_square\", \"area\", \"reverse_area\", \"volume\", \"reverse_volume\".")
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

        return sizing_column, sizeScale, size_range, alpha, nodeLabels, fontSize, keepSingletons

    def __filter_paramCheck(self, column, threshold, operator, sign):

        g = self.__g
        col_list = list(g.nodes[list(g.nodes.keys())[0]].keys())[:-2] + ['none']

        if column not in col_list:
            print("Error: Filter column not valid. Choose one of {}.".format(', '.join(col_list)))
            sys.exit()
        else:

            if column != 'none':
                for idx, node in enumerate(g.nodes()):
                    try:
                        float(g.node[node][column])
                    except ValueError:
                        print("Error: Filter column contains invalid values. Choose a filter column containing float or integer values.")
                        sys.exit()

        if not isinstance(threshold, float):
            if not isinstance(threshold, int):
                print("Error: Filter threshold is not valid. Choose a float or integer value.")
                sys.exit()
            elif threshold == 0:
                print("Error: Filter threshold should not be zero. Choose a value close to zero or above.")
                sys.exit()
        elif threshold == 0.0:
            print("Error: Filter threshold should not be zero. Choose a value close to zero or above.")
            sys.exit()

        if operator not in ["<", ">", "<=", ">="]:
            print("Error: Operator not valid. Choose either \"<\", \">\", \"<=\" or \">=\".")
            sys.exit()

        if sign.lower() not in ["pos", "neg", "both"]:
            print("Error: Sign not valid. Choose either \"pos\", \"neg\", or \"both\".")
            sys.exit()

        return column, threshold, operator, sign