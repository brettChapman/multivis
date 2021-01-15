import sys
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
from .utils import *

class Edge:
    """ Class for edgeBundle and base class for network.

        Initial_Parameters
        ----------
        peaktable : Pandas dataframe containing peak data. Must contain 'Name' and 'Label'.
        datatable : Pandas dataframe matrix containing scores
        pvalues : Pandas dataframe matrix containing score/similarity pvalues (if available, otherwise set to None)

        Methods
        -------
        set_params : Set parameters
            filter_type: The value type to filter the data on (default: 'pvalue')
            hard_threshold: Value to filter the data on (default: 0.005)
            internalScores: Include scores within blocks if building multi-block network (default: False)
            sign: The sign of the score/similarity to filter on ('pos', 'neg' or 'both') (default: 'both')

        build : Builds the nodes and edges.
        getNodes : Returns a Pandas dataframe of all nodes.
        getEdges : Returns a Pandas dataframe of all edges.
    """

    def __init__(self, peaktable, datatable, pvalues):

        self.__peaktable = self.__checkPeakTable(self.__checkData(peaktable))
        self.__datatable = self.__checkData(datatable)

        if pvalues is not None:
            self.__pvalues = self.__checkData(pvalues)
        else:
            self.__pvalues = pvalues

        self.__setNodes(pd.DataFrame())
        self.__setEdges(pd.DataFrame())

        self.set_params()

    def set_params(self, filter_type='pvalue', hard_threshold=0.005, internalScores=False, sign='both'):

        filter_type, hard_threshold, internalScores, sign = self.__paramCheck(filter_type, hard_threshold, internalScores, sign)

        self.__filter_type = filter_type;
        self.__hard_threshold = hard_threshold;
        self.__internalScores = internalScores;
        self.__sign = sign;

    def build(self):

        peaktable = self.__peaktable
        datatable = self.__datatable
        pvalues = self.__pvalues

        filter_type = self.__filter_type
        hard_threshold = self.__hard_threshold
        sign = self.__sign

        nodes = pd.DataFrame();
        edges = pd.DataFrame();

        if 'Block' in peaktable.columns:
            index_blocks = peaktable[peaktable['Name'].isin(list(datatable.index))].Block.unique()
            column_blocks = peaktable[peaktable['Name'].isin(list(datatable.columns))].Block.unique()
        else:
            index_blocks = ['#no_multiple_blocks']
            column_blocks = ['#no_multiple_blocks']

        for idx, index_block in enumerate(index_blocks):

            nodes, scoreBlocks_index, pvalBlocks_index = self.__scoreBlockIndex(nodes, peaktable, datatable, pvalues, index_blocks, index_block)

            if set(list(datatable.index)) == set(list(datatable.columns)):
                iter_idx = idx;
            else:
                iter_idx = 0;

            for column_block in column_blocks[iter_idx:]:

                if pvalues is None:
                    filter_type = 'score';

                if self.__internalScores:

                    nodes, scoreBlocks_column, pvalBlocks_column = self.__scoreBlockColumn(nodes, peaktable, scoreBlocks_index, pvalBlocks_index, column_blocks, column_block);

                    if edges.empty:
                        edges = self.__buildEdges(nodes, scoreBlocks_column, pvalBlocks_column, index_block, column_block, filter_type, hard_threshold, sign)
                    else:
                        dat_edges = self.__buildEdges(nodes, scoreBlocks_column, pvalBlocks_column, index_block, column_block, filter_type, hard_threshold, sign)
                        edges = pd.concat([edges, dat_edges], sort=False).reset_index(drop=True)
                else:

                    if index_block != column_block:

                        nodes, scoreBlocks_column, pvalBlocks_column = self.__scoreBlockColumn(nodes, peaktable, scoreBlocks_index, pvalBlocks_index, column_blocks, column_block);

                        if edges.empty:
                            edges = self.__buildEdges(nodes, scoreBlocks_column, pvalBlocks_column, index_block, column_block, filter_type, hard_threshold, sign)
                        else:
                            dat_edges = self.__buildEdges(nodes, scoreBlocks_column, pvalBlocks_column, index_block, column_block, filter_type, hard_threshold, sign)
                            edges = pd.concat([edges, dat_edges], sort=False).reset_index(drop=True)
                    else:
                        if ((len(index_blocks) == 1) and (len(column_blocks) == 1)):
                            if ((index_blocks[0] == '#no_multiple_blocks') and (column_blocks[0] == '#no_multiple_blocks')):
                                edges = self.__buildEdges(nodes, scoreBlocks_index, pvalBlocks_index, index_block, column_block, filter_type, hard_threshold, sign)

        self.__setNodes(nodes)
        self.__setEdges(edges)

    def getNodes(self):

        return self.__nodes

    def getEdges(self):

        return self.__edges

    def __checkData(self, df):

        if not isinstance(df, pd.DataFrame):
            print("Error: A dataframe was not entered. Please check your data.")

        return df

    def __checkPeakTable(self, PeakTable):

        if "Name" not in PeakTable.columns:
            print("Error: \"Name\" column not in Peak Table. Please check your data.")
            sys.exit()

        if "Label" not in PeakTable.columns:
            print("Error: \"Label\" column not in Peak Table. Please check your data.")
            sys.exit()

        return PeakTable

    def __paramCheck(self, filter_type, hard_threshold, internalScores, sign):

        if filter_type.lower() not in ["pvalue", "score"]:
            print("Error: Filter type not valid. Choose either \"Pvalue\" or \"Score\".")
            sys.exit()

        if not isinstance(hard_threshold, float):
            if not isinstance(hard_threshold, int):
                print("Error: Hard threshold is not valid. Choose a float or integer value.")
                sys.exit()

        if not type(internalScores) == bool:
            print("Error: Internal scores not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if sign.lower() not in ["pos", "neg", "both"]:
            print("Error: Sign is not valid. Choose either \"pos\" or \"neg\" or \"both\".")
            sys.exit()

        return filter_type, hard_threshold, internalScores, sign

    def __scoreBlockIndex(self, nodes, peaks, data, pvalues, blocks, index_block):

        node_data = []

        if blocks[0] != '#no_multiple_blocks':
            for col in peaks.columns:
                node_data.append(list(peaks[peaks['Block'] == index_block][col].values))

            index_block_names = list(peaks[peaks['Block'] == index_block]['Name'].values)
        else:
            for col in peaks.columns:
                node_data.append(list(peaks[col].values))

            index_block_names = list(peaks['Name'].values)

        if blocks[0] == '#no_multiple_blocks':
            scoreBlocks_index = data
        else:
            scoreBlocks_index = data[data.index.isin(index_block_names)]

        if pvalues is not None:
            if blocks[0] == '#no_multiple_blocks':
                pvalBlocks_index = pvalues
            else:
                pvalBlocks_index = pvalues[pvalues.index.isin(index_block_names)]
        else:
            pvalBlocks_index = None;

        if nodes.empty:
            nodes = pd.DataFrame(np.column_stack(node_data), columns=peaks.columns)
            nodes['Block'] = index_block
        else:
            addedBlocks = list(np.unique(nodes['Block'].values))

            if index_block not in addedBlocks:
                dat = pd.DataFrame(np.column_stack(node_data), columns=peaks.columns)
                dat['Block'] = index_block

                nodes = pd.concat([nodes, dat], sort=False).reset_index(drop=True)

        if blocks[0] == '#no_multiple_blocks':
            nodes = nodes.drop(columns="Block")

        return nodes, scoreBlocks_index, pvalBlocks_index

    def __scoreBlockColumn(self, nodes, peaks, data, pvalues, blocks, column_block):

        node_data = []

        if blocks[0] != '#no_multiple_blocks':

            for col in peaks.columns:
                node_data.append(list(peaks[peaks['Block'] == column_block][col].values))

            column_block_names = list(peaks[peaks['Block'] == column_block]['Name'].values)
        else:
            for col in peaks.columns:
                node_data.append(list(peaks[col].values))

            column_block_names = list(peaks['Name'].values)

        scoreBlocks_column = data[column_block_names].astype(float)

        if pvalues is not None:
            pvalBlocks_column = pvalues[column_block_names].astype(float)
        else:
            pvalBlocks_column = None;

        if nodes.empty:
            nodes = pd.DataFrame(np.column_stack(node_data), columns=peaks.columns)
            nodes['Block'] = column_block
        else:
            addedBlocks = list(np.unique(nodes['Block'].values))

            if column_block not in addedBlocks:
                dat = pd.DataFrame(np.column_stack(node_data), columns=peaks.columns)
                dat['Block'] = column_block

                nodes = pd.concat([nodes, dat], sort=False).reset_index(drop=True)

        return nodes, scoreBlocks_column, pvalBlocks_column

    def __buildEdges(self, nodes, SCORE, PVAL, start_block, end_block, filter_type, hard_threshold, sign):

        if 'Block' in nodes.columns:
            blocks = list(nodes['Block'].unique())
        else:
            blocks = ['#no_multiple_blocks']

        if blocks[0] != '#no_multiple_blocks':
            start_block_nodes = nodes[nodes['Block'] == start_block]
            end_block_nodes = nodes[nodes['Block'] == end_block]
        else:
            start_block_nodes = nodes
            end_block_nodes = nodes

        def __score(start_block_nodes, end_block_nodes, SCORE, PVAL, start_block, end_block, blocks, hard_threshold):

            score_cols = SCORE.columns
            score_rows = SCORE.index

            start_block_indexes = list(start_block_nodes.index)
            end_block_indexes = list(end_block_nodes.index)

            start_block_names = list(start_block_nodes['Name'])
            end_block_names = list(end_block_nodes['Name'])

            start_block_labels = list(start_block_nodes['Label'])
            end_block_labels = list(end_block_nodes['Label'])

            e = []

            for i_idx in range(0, len(score_rows)):

                start_name = score_rows[i_idx]

                if set(list(SCORE.columns)) == set(list(SCORE.index)):
                    col_idx = i_idx
                else:
                    col_idx = 0;
                    columns_set = frozenset(list(SCORE.columns))
                    index_set = frozenset(list(SCORE.index))

                    start_block_names = [x for x in start_block_names if x in index_set]
                    end_block_names = [x for x in end_block_names if x in columns_set]

                    start_block_labels = list(start_block_nodes[start_block_nodes['Name'].isin(start_block_names)]['Label'])
                    end_block_labels = list(end_block_nodes[end_block_nodes['Name'].isin(end_block_names)]['Label'])

                    start_block_indexes = list(start_block_nodes[start_block_nodes['Name'].isin(start_block_names)].index)
                    end_block_indexes = list(end_block_nodes[end_block_nodes['Name'].isin(end_block_names)].index)

                for j_idx in range(col_idx, len(score_cols)):

                    if (abs(SCORE.values[i_idx, j_idx]) > hard_threshold):

                        end_name = score_cols[j_idx]

                        start_label = start_block_labels[i_idx]
                        end_label = end_block_labels[j_idx]

                        start_index = start_block_indexes[i_idx]
                        end_index = end_block_indexes[j_idx]

                        if start_index != end_index:
                            if PVAL is None:

                                if blocks[0] != '#no_multiple_blocks':
                                    b = [start_index, start_name, start_label, start_block, end_index, end_name, end_label, end_block, SCORE.values[i_idx, j_idx], np.sign(SCORE.values[i_idx, j_idx])];
                                else:
                                    b = [start_index, start_name, start_label, end_index, end_name, end_label, SCORE.values[i_idx, j_idx], np.sign(SCORE.values[i_idx, j_idx])];
                            else:

                                if blocks[0] != '#no_multiple_blocks':
                                    b = [start_index, start_name, start_label, start_block, end_index, end_name, end_label, end_block, SCORE.values[i_idx, j_idx], np.sign(SCORE.values[i_idx, j_idx]), PVAL.values[i_idx, j_idx]];
                                else:
                                    b = [start_index, start_name, start_label, end_index, end_name, end_label, SCORE.values[i_idx, j_idx], np.sign(SCORE.values[i_idx, j_idx]), PVAL.values[i_idx, j_idx]];
                            e.append(b)

            if PVAL is None:

                if blocks[0] != '#no_multiple_blocks':
                    score = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_label', 'start_block', 'end_index', 'end_name', 'end_label', 'end_block', 'score', 'sign'])
                else:
                    score = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_label', 'end_index', 'end_name', 'end_label', 'score', 'sign'])
            else:

                if blocks[0] != '#no_multiple_blocks':
                    score = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_label', 'start_block', 'end_index', 'end_name', 'end_label', 'end_block', 'score', 'sign', 'pvalue'])
                else:
                    score = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_label', 'end_index', 'end_name', 'end_label', 'score', 'sign', 'pvalue'])

            return score

        def __pval(start_block_nodes, end_block_nodes, SCORE, PVAL, start_block, end_block, blocks, hard_threshold):

            score_cols = SCORE.columns
            score_rows = SCORE.index

            start_block_indexes = list(start_block_nodes.index)
            end_block_indexes = list(end_block_nodes.index)

            start_block_names = list(start_block_nodes['Name'])
            end_block_names = list(end_block_nodes['Name'])

            start_block_labels = list(start_block_nodes['Label'])
            end_block_labels = list(end_block_nodes['Label'])

            e = []

            for i_idx in range(0, len(score_rows)):

                start_name = score_rows[i_idx]

                if set(list(SCORE.columns)) == set(list(SCORE.index)):
                    col_idx = i_idx
                else:
                    col_idx = 0;
                    columns_set = frozenset(list(SCORE.columns))
                    index_set = frozenset(list(SCORE.index))

                    start_block_names = [x for x in start_block_names if x in index_set]
                    end_block_names = [x for x in end_block_names if x in columns_set]

                    start_block_labels = list(start_block_nodes[start_block_nodes['Name'].isin(start_block_names)]['Label'])
                    end_block_labels = list(end_block_nodes[end_block_nodes['Name'].isin(end_block_names)]['Label'])

                    start_block_indexes = list(start_block_nodes[start_block_nodes['Name'].isin(start_block_names)].index)
                    end_block_indexes = list(end_block_nodes[end_block_nodes['Name'].isin(end_block_names)].index)

                for j_idx in range(col_idx, len(score_cols)):

                    end_name = score_cols[j_idx]

                    start_label = start_block_labels[i_idx]
                    end_label = end_block_labels[j_idx]

                    start_index = start_block_indexes[i_idx]
                    end_index = end_block_indexes[j_idx]

                    if start_index != end_index:
                        if PVAL is None:

                            if blocks[0] != '#no_multiple_blocks':
                                b = [start_index, start_name, start_label, start_block, end_index, end_name, end_label, end_block, SCORE.values[i_idx, j_idx], np.sign(SCORE.values[i_idx, j_idx])];
                            else:
                                b = [start_index, start_name, start_label, end_index, end_name, end_label, SCORE.values[i_idx, j_idx], np.sign(SCORE.values[i_idx, j_idx])];

                            e.append(b)
                        else:
                            if (PVAL.values[i_idx, j_idx] < hard_threshold):

                                if blocks[0] != '#no_multiple_blocks':
                                    b = [start_index, start_name, start_label, start_block, end_index, end_name, end_label, end_block, SCORE.values[i_idx, j_idx], np.sign(SCORE.values[i_idx, j_idx]), PVAL.values[i_idx, j_idx]]
                                else:
                                    b = [start_index, start_name, start_label, end_index, end_name, end_label, SCORE.values[i_idx, j_idx], np.sign(SCORE.values[i_idx, j_idx]), PVAL.values[i_idx, j_idx]];

                                e.append(b)

            if PVAL is None:

                if blocks[0] != '#no_multiple_blocks':
                    pval = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_label', 'start_block', 'end_index', 'end_name', 'end_label', 'end_block', 'score', 'sign'])
                else:
                    pval = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_label', 'end_index', 'end_name', 'end_label', 'score', 'sign'])
            else:

                if blocks[0] != '#no_multiple_blocks':
                    pval = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_label', 'start_block', 'end_index', 'end_name', 'end_label', 'end_block', 'score', 'sign', 'pvalue'])
                else:
                    pval = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_label', 'end_index', 'end_name', 'end_label', 'score', 'sign', 'pvalue'])

            return pval

        options = {'score': __score(start_block_nodes, end_block_nodes, SCORE, PVAL, start_block, end_block, blocks, hard_threshold), 'pvalue': __pval(start_block_nodes, end_block_nodes, SCORE, PVAL, start_block, end_block, blocks, hard_threshold)}

        edges = pd.DataFrame()

        if filter_type.lower() in options:
            edges = options[filter_type.lower()];
        else:
            print ("Error: wrong score type specified. Valid entries are 'Score' or 'Pvalue'.")

        if sign.lower() == "pos":
            edges = edges[edges['sign'] > 0].reset_index(drop=True)
        elif sign.lower() == "neg":
            edges = edges[edges['sign'] < 0].reset_index(drop=True)

        return edges

    def __setNodes(self, nodes):

        self.__nodes = nodes

    def __setEdges(self, edges):

        self.__edges = edges