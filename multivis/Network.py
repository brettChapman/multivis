import sys
import pandas as pd
import numpy as np
import networkx as nx
from .Edge import Edge
from .utils import *

class Network(Edge):
    """Class for Network. Inherits from Edge.

        Initial_Parameters
        ----------
        peaktable : Pandas dataframe containing peak data. Must contain 'Name' and 'Label'.
        similarities : Pandas dataframe matrix containing similarity scores
        pvalues : Pandas dataframe matrix containing similarity pvalues

        Methods
        -------
        set_params : Set parameters -
            filter_type: The value type to filter similarities on (default: 'pvalue')
            hard_threshold: Value to filter similarities on (default: 0.005)
            link_type: The value type to represent links in the network (default: 'score')
            internalSimilarities: Include similarities within blocks if building multi-block network (default: False)
            sign: The sign of the similarity score to filter on ('pos', 'neg' or 'both') (default: 'both')

        build : Builds nodes, edges and NetworkX graph.
        getNetworkx : Returns a NetworkX graph.
        getLinkType : Returns the link type parameter used in building the network.
    """

    def __init__(self, peaktable, similarities, pvalues):

        Edge.__init__(self, peaktable, similarities, pvalues)

        self.set_params()

    def set_params(self, filter_type='pvalue', hard_threshold=0.005, link_type='score', internalSimilarities=False, sign='both'):

        Edge.set_params(self, filter_type, hard_threshold, internalSimilarities, sign)

        link_type = self.__paramCheck(link_type)

        self.__setLinkType(link_type)

    def build(self):

        Edge.build(self)

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

        if 'Block' in nodes.columns:
            blocks = list(nodes['Block'].unique())
        else:
            blocks = [1]

        g = nx.Graph()

        if "pvalue" in edges.columns:

            if len(blocks) > 1:
                #for source_index, _, _, source, source_block, target_index, _, _, target, target_block, score, _, pvalue in edges.values:
                for source_index, _, source, source_block, target_index, _, target, target_block, score, _, pvalue in edges.values:
                    if self.getLinkType().lower() == "pvalue":
                        g.add_edge(source_index, target_index, weight=pvalue)
                    elif self.getLinkType().lower() == "score":
                        g.add_edge(source_index, target_index, weight=score)
            else:
                #for source_index, _, _, source, target_index, _, _, target, score, _, pvalue in edges.values:
                for source_index, _, source, target_index, _, target, score, _, pvalue in edges.values:
                    if self.getLinkType().lower() == "pvalue":
                        g.add_edge(source_index, target_index, weight=pvalue)
                    elif self.getLinkType().lower() == "score":
                        g.add_edge(source_index, target_index, weight=score)
        else:

            if len(blocks) > 1:
                #for source_index, _, _, source, source_block, target_index, _, _, target, target_block, score, _ in edges.values:
                for source_index, _, source, source_block, target_index, _, target, target_block, score, _ in edges.values:
                    g.add_edge(source_index, target_index, weight=score)
            else:
                #for source_index, _, _, source, target_index, _, _, target, score, _ in edges.values:
                for source_index, _, source, target_index, _, target, score, _ in edges.values:
                    g.add_edge(source_index, target_index, weight=score)

        nx.set_node_attributes(g, nodes.to_dict('index'))

        self.__setNetworkx(g)

    def __setNetworkx(self, g):

        self.__g = g

    def __setLinkType(self, link_type):

        self.__link_type = link_type