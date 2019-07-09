import sys
import pandas as pd
import numpy as np
import networkx as nx
from .Edge import Edge
from .utils import *

class Network(Edge):
    """Class for Network. Inherits from Edge."""

    def __init__(self, peaks, scores, pvalues):

        Edge.__init__(self, peaks, scores, pvalues)

        self.set_params()

    def run(self):

        self.runEdges()

        self.__networkXEdges()

    def set_params(self, filterScoreType='Pvalue', hard_threshold=0.005, link_type='Score', lengthScale='linear', length_range=(1,10), internalCorrelation=False, sign="both", verbose=0):

        Edge.set_params(self, filterScoreType, hard_threshold, internalCorrelation, sign, verbose)

        lengthScale, length_range, link_type = self.__paramCheck(lengthScale, length_range, link_type)

        self.__lengthScale = lengthScale
        self.__length_range = length_range
        self.__setLinkType(link_type)

    def __paramCheck(self, lengthScale, length_range, link_type):

        if lengthScale.lower() not in ["linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square"]:
            print("Error: Length scale type not valid. Choose either \"linear\", \"reverse_linear\", \"log\", \"reverse_log\", \"square\", \"reverse_square\".")
            sys.exit()

        if not isinstance(length_range, tuple):
            print("Error: Length range is not valid. Choose a list of length 2.")
            sys.exit()
        else:
            for length in length_range:
                if not isinstance(length, float):
                    if not isinstance(length, int):
                        print("Error: Length range items not valid. Choose a float or integer value.")
                        sys.exit()

        if link_type.lower() not in ["pvalue", "score"]:
            print("Error: Link type not valid. Choose either \"Pvalue\" or \"Score\".")
            sys.exit()

        return lengthScale, length_range, link_type

    def __networkXEdges(self):

        nodes = self.getNodes()
        edges = self.getEdges()

        if 'Group' in nodes.columns:
            blocks = list(nodes['Group'].unique())
        else:
            blocks = [1]

        g = nx.Graph()

        edge_dist = np.array(list(edges[self.getLinkType()].values))
        edge_dist = np.array([x for x in list(range_scale(edge_dist, 1, 10))])

        if self.__lengthScale.lower() == 'linear':
            edge_distance = [x for x in list(range_scale(edge_dist, self.__length_range[0], self.__length_range[1]))]
        if self.__lengthScale.lower() == 'reverse_linear':
            edge_dist = np.divide(1, edge_dist)
            edge_distance = [x for x in list(range_scale(edge_dist, self.__length_range[0], self.__length_range[1]))]
        elif self.__lengthScale.lower() == 'log':
            edge_dist = np.log(edge_dist)
            edge_distance = [x for x in list(range_scale(edge_dist, self.__length_range[0], sellf.__length_range[1]))]
        elif self.__lengthScale.lower() == 'reverse_log':
            edge_dist = np.divide(1, edge_dist)
            edge_dist = np.log(edge_dist)
            edge_distance = [x for x in list(range_scale(edge_dist, self.__length_range[0], self.__length_range[1]))]
        elif self.__lengthScale.lower() == 'square':
            edge_dist = np.square(edge_dist)
            edge_distance = [x for x in list(range_scale(edge_dist, self.__length_range[0], self.__length_range[1]))]
        elif self.__lengthScale.lower() == 'reverse_square':
            edge_dist = np.divide(1, edge_dist)
            edge_dist = np.square(edge_dist)
            edge_distance = [x for x in list(range_scale(edge_dist, self.__length_range[0], self.__length_range[1]))]

        edges = edges.assign(length=edge_distance)

        if "Pvalue" in edges.columns:

            if len(blocks) > 1:
                for source_index, _, _, source, source_block, target_index, _, _, target, target_block, score, _, pvalue, length in edges.values:

                    if self.getLinkType().lower() == "pvalue":
                        g.add_edge(source_index, target_index, weight=pvalue, len=length)
                    elif self.getLinkType().lower() == "score":
                        g.add_edge(source_index, target_index, weight=score, len=length)
            else:
                for source_index, _, _, source, target_index, _, _, target, score, _, pvalue, length in edges.values:

                    if self.getLinkType().lower() == "pvalue":
                        g.add_edge(source_index, target_index, weight=pvalue, len=length)
                    elif self.getLinkType().lower() == "score":
                        g.add_edge(source_index, target_index, weight=score, len=length)
        else:

            if len(blocks) > 1:
                for source_index, _, _, source, source_block, target_index, _, _, target, target_block, score, _, length in edges.values:
                    g.add_edge(source_index, target_index, weight=score, len=length)
            else:
                for source_index, _, _, source, target_index, _, _, target, score, _, length in edges.values:
                    g.add_edge(source_index, target_index, weight=score, len=length)

        nodes['x_position'] = 0
        nodes['y_position'] = 0

        nx.set_node_attributes(g, nodes.to_dict('index'))

        #for idx, indexName in enumerate(nodes.index):

            #add pval, rho, other things to size nodes by. can we add everything in nodes dataframe?
            #https://stackoverflow.com/questions/42558165/load-nodes-with-attributes-and-edges-from-dataframe-to-networkx

            #add edges, then set node attributes
            #nx.set_node_attributes(G, pd.Series(nodes.gender, index=nodes.node).to_dict(), 'gender')

         #   if 'group' in nodes.columns:
         #       g.add_node(indexName, label=nodes['label'].values[idx]
         #              , name=nodes['name'].values[idx]
         #              , group=nodes['group'].values[idx]
         #              , color=nodes['color'].values[idx])
         #   else:
         #       g.add_node(indexName, label=nodes['label'].values[idx]
         #                  , name=nodes['name'].values[idx]
         #                  , color=nodes['color'].values[idx])

        self.__setNetworkx(g)

    def __setNetworkx(self, g):

        self.__g = g

    def getNetworkx(self):

        return self.__g

    def __setLinkType(self, link_type):

        self.__link_type = link_type

    def getLinkType(self):

        return self.__link_type