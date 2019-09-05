import sys
import pandas as pd
import numpy as np
import networkx as nx
from .Edge import Edge
from .utils import *

class Network(Edge):
    """Class for Network. Inherits from Edge.

        Parameters
        ----------
        peaktable : Pandas dataframe containing peak data
        scores : Pandas dataframe containing correlation coefficients
        pvalues : Pandas dataframe containing correlation pvalues

        Methods
        -------
        set_params : Set parameters - filter score type, hard threshold, internal correlation flag and sign type.
        run : Builds nodes, edges and NetworkX graph.
        getNetworkx : Returns a NetworkX graph.
        getLinkType : Returns the link type parameter used in building the network.
    """

    def __init__(self, peaks, scores, pvalues):

        Edge.__init__(self, peaks, scores, pvalues)

        self.set_params()

    def set_params(self, filterScoreType='Pvalue', hard_threshold=0.005, link_type='Score', internalCorrelation=False, sign="both"):

        Edge.set_params(self, filterScoreType, hard_threshold, internalCorrelation, sign)

        link_type = self.__paramCheck(link_type)

        self.__setLinkType(link_type)

    def run(self):

        Edge.run(self)

        self.__networkXEdges()

    def getNetworkx(self):

        return self.__g

    def getLinkType(self):

        return self.__link_type

    def __paramCheck(self, link_type):

        if link_type.lower() not in ["pvalue", "score"]:
            print("Error: Link type not valid. Choose either \"Pvalue\" or \"Score\".")
            sys.exit()

        return link_type

    def __networkXEdges(self):

        nodes = self.getNodes()
        edges = self.getEdges()

        if 'Group' in nodes.columns:
            blocks = list(nodes['Group'].unique())
        else:
            blocks = [1]

        g = nx.Graph()

        if "Pvalue" in edges.columns:

            if len(blocks) > 1:
                for source_index, _, _, source, source_block, target_index, _, _, target, target_block, score, _, pvalue in edges.values:
                    if self.getLinkType().lower() == "pvalue":
                        g.add_edge(source_index, target_index, weight=pvalue)
                    elif self.getLinkType().lower() == "score":
                        g.add_edge(source_index, target_index, weight=score)
            else:
                for source_index, _, _, source, target_index, _, _, target, score, _, pvalue in edges.values:
                    if self.getLinkType().lower() == "pvalue":
                        g.add_edge(source_index, target_index, weight=pvalue)
                    elif self.getLinkType().lower() == "score":
                        g.add_edge(source_index, target_index, weight=score)
        else:

            if len(blocks) > 1:
                for source_index, _, _, source, source_block, target_index, _, _, target, target_block, score, _ in edges.values:
                    g.add_edge(source_index, target_index, weight=score)
            else:
                for source_index, _, _, source, target_index, _, _, target, score, _ in edges.values:
                    g.add_edge(source_index, target_index, weight=score)

        nx.set_node_attributes(g, nodes.to_dict('index'))

        self.__setNetworkx(g)

    def __setNetworkx(self, g):

        self.__g = g

    def __setLinkType(self, link_type):

        self.__link_type = link_type