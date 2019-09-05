import sys
import pandas as pd
import numpy as np
import networkx as nx
from .utils import *

class Edge:
    """ Class for edgeBundle and base class for network.

        Parameters
        ----------
        peaktable : Pandas dataframe containing peak data
        scores : Pandas dataframe containing correlation coefficients
        pvalues : Pandas dataframe containing correlation pvalues

        Methods
        -------
        set_params : Set parameters - filter score type, hard threshold, internal correlation flag and sign type.
        run : Builds the nodes and edges.
        getNodes : Returns a Pandas dataframe of all nodes.
        getEdges : Returns a Pandas dataframe of all edges.
    """

    def __init__(self, peaktable, scores, pvalues):

        self.__peaks = self.__checkPeaks(self.__checkData(peaktable));
        self.__scores = self.__checkData(scores);
        self.__pvalues = self.__checkData(pvalues);

        self.__setNodes(pd.DataFrame())
        self.__setEdges(pd.DataFrame())

        self.set_params()

    def set_params(self, filterScoreType='Pvalue', hard_threshold=0.005, internalCorrelation=False, sign="both"):

        filterScoreType, hard_threshold, internalCorrelation, sign = self.__paramCheck(filterScoreType, hard_threshold, internalCorrelation, sign)

        self.__filterScoreType = filterScoreType;
        self.__hard_threshold = hard_threshold;
        self.__internalCorrelation = internalCorrelation;
        self.__sign = sign;

    def run(self):

        peaks = self.__peaks
        scores = self.__scores
        pvalues = self.__pvalues

        filterScoreType = self.__filterScoreType
        hard_threshold = self.__hard_threshold
        sign = self.__sign

        if 'Block' in peaks.columns:
            blocks = list(peaks['Block'].unique())
        else:
            blocks = [1]

        nodes = pd.DataFrame();
        edges = pd.DataFrame();

        for idx, block1 in enumerate(blocks):

            nodes, scoreBlocks_blocked1, pvalBlocks_blocked1, block1_labels = self.__scoreBlock1(nodes, peaks, scores, pvalues, blocks, block1)

            for block2 in blocks[idx:]:

                if pvalues is None:
                    filterScoreType = 'Score';

                if self.__internalCorrelation:

                    nodes, scoreBlocks_blocked2, pvalBlocks_blocked2 = self.__scoreBlock2(nodes, peaks, scoreBlocks_blocked1, pvalBlocks_blocked1, blocks, block2, block1_labels);

                    if edges.empty:
                        edges = self.__buildEdges(nodes, scoreBlocks_blocked2, pvalBlocks_blocked2, block1, block2, filterScoreType, hard_threshold, sign)
                    else:
                        dat_edges = self.__buildEdges(nodes, scoreBlocks_blocked2, pvalBlocks_blocked2, block1, block2, filterScoreType, hard_threshold, sign)
                        edges = pd.concat([edges, dat_edges], sort=False).reset_index(drop=True)
                else:

                    if block1 != block2:

                        nodes, scoreBlocks_blocked2, pvalBlocks_blocked2 = self.__scoreBlock2(nodes, peaks, scoreBlocks_blocked1, pvalBlocks_blocked1, blocks, block2, block1_labels);

                        if edges.empty:
                            edges = self.__buildEdges(nodes, scoreBlocks_blocked2, pvalBlocks_blocked2, block1, block2, filterScoreType, hard_threshold, sign)
                        else:
                            dat_edges = self.__buildEdges(nodes, scoreBlocks_blocked2, pvalBlocks_blocked2, block1, block2, filterScoreType, hard_threshold, sign)
                            edges = pd.concat([edges, dat_edges], sort=False).reset_index(drop=True)
                    else:
                        if len(blocks) == 1:
                            edges = self.__buildEdges(nodes, scoreBlocks_blocked1, pvalBlocks_blocked1, block1, block2, filterScoreType, hard_threshold, sign)

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

    def __checkPeaks(self, Peaks):

        if "Name" not in Peaks.columns:
            print("Error: \"Name\" column not in Peak Table. Please check your data.")
            sys.exit()

        if "Label" not in Peaks.columns:
            print("Error: \"Label\" column not in Peak Table. Please check your data.")
            sys.exit()

        if "Color" not in Peaks.columns:
            print("Error: \"Color\" column not in Peak Table. Please check your data.")
            sys.exit()

        return Peaks

    def __paramCheck(self, filterScoreType, hard_threshold, internalCorrelation, sign):

        if filterScoreType.lower() not in ["pvalue", "score"]:
            print("Error: Filter score type not valid. Choose either \"Pvalue\" or \"Score\".")
            sys.exit()

        if not isinstance(hard_threshold, float):
            if not isinstance(hard_threshold, int):
                print("Error: Hard threshold is not valid. Choose a float or integer value.")
                sys.exit()

        if not type(internalCorrelation) == bool:
            print("Error: Internal correlation not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if sign.lower() not in ["pos", "neg", "both"]:
            print("Error: Sign is not valid. Choose either \"pos\" or \"neg\" or \"both\".")
            sys.exit()

        return filterScoreType, hard_threshold, internalCorrelation, sign

    def __scoreBlock1(self, nodes, peaks, scores, pvalues, blocks, block1):

        node_data = []

        if len(blocks) > 1:

            for col in peaks.columns:
                node_data.append(list(peaks[peaks['Block'] == block1][col].values))

            block1_labels = list(peaks[peaks['Block'] == block1]['Label'].values)
            block1_names = list(peaks[peaks['Block'] == block1]['Name'].values)
            #block1_colors = list(peaks[peaks['Block'] == block1]['Color'].values)
        else:
            for col in peaks.columns:
                node_data.append(list(peaks[col].values))

            block1_labels = list(peaks['Label'].values)
            block1_names = list(peaks['Name'].values)
            #block1_colors = list(peaks['Color'].values)

        if len(blocks) == 1:

            scoreBlocks_blocked1 = scores

            scoreBlocks_blocked1.index = block1_labels
            scoreBlocks_blocked1.columns = block1_labels
        else:
            scoreBlocks_blocked1 = scores[scores.index.isin(block1_names)]

        if pvalues is not None:
            if len(blocks) == 1:

                pvalBlocks_blocked1 = pvalues

                pvalBlocks_blocked1.index = block1_labels
                pvalBlocks_blocked1.columns = block1_labels
            else:
                pvalBlocks_blocked1 = pvalues[pvalues.index.isin(block1_names)]

        else:
            pvalBlocks_blocked1 = None;

        if nodes.empty:
            nodes = pd.DataFrame(np.column_stack(node_data), columns=peaks.columns)#['label', 'name', 'color'])
            nodes['Group'] = block1
        else:
            addedBlocks = list(np.unique(nodes['Group'].values))

            if block1 not in addedBlocks:
                dat = pd.DataFrame(np.column_stack(node_data), columns=peaks.columns)#['label', 'name', 'color'])
                dat['Group'] = block1

                nodes = pd.concat([nodes, dat], sort=False).reset_index(drop=True)

        if not len(blocks) > 1:
            nodes = nodes.drop(columns="Group")

        return nodes, scoreBlocks_blocked1, pvalBlocks_blocked1, block1_labels

    def __scoreBlock2(self, nodes, peaks, scoreBlocks_blocked1, pvalBlocks_blocked1, blocks, block2, block1_labels):

        node_data = []

        if len(blocks) > 1:

            for col in peaks.columns:
                node_data.append(list(peaks[peaks['Block'] == block2][col].values))

            block2_labels = list(peaks[peaks['Block'] == block2]['Label'].values)
            block2_names = list(peaks[peaks['Block'] == block2]['Name'].values)
            #block2_colors = list(peaks[peaks['Block'] == block2]['Color'].values)
        else:

            for col in peaks.columns:
                node_data.append(list(peaks[col].values))

            block2_labels = list(peaks['Label'].values)
            block2_names = list(peaks['Name'].values)
            #block2_colors = list(peaks['Color'].values)

        scoreBlocks_blocked2 = scoreBlocks_blocked1[block2_names].astype(float)

        scoreBlocks_blocked2.index = block1_labels
        scoreBlocks_blocked2.columns = block2_labels

        if pvalBlocks_blocked1 is not None:
            pvalBlocks_blocked2 = pvalBlocks_blocked1[block2_names].astype(float)
            pvalBlocks_blocked2.index = block1_labels
            pvalBlocks_blocked2.columns = block2_labels
        else:
            pvalBlocks_blocked2 = None;

        if nodes.empty:
            nodes = pd.DataFrame(np.column_stack(node_data), columns=peaks.columns)#'label', 'name', 'color'])
            nodes['Group'] = block2
        else:
            addedBlocks = list(np.unique(nodes['Group'].values))

            if block2 not in addedBlocks:
                dat = pd.DataFrame(np.column_stack(node_data), columns=peaks.columns)
                dat['Group'] = block2

                nodes = pd.concat([nodes, dat], sort=False).reset_index(drop=True)

        return nodes, scoreBlocks_blocked2, pvalBlocks_blocked2

    def __buildEdges(self, nodes, SCORE, PVAL, block1, block2, filterScoreType, hard_threshold, sign):

        if 'Group' in nodes.columns:
            blocks = list(nodes['Group'].unique())
        else:
            blocks = [1]

        if len(blocks) > 1:
            block1_nodes = nodes[nodes['Group'] == block1]
            block2_nodes = nodes[nodes['Group'] == block2]
        else:
            block1_nodes = nodes
            block2_nodes = nodes

        def __score(block1_nodes, block2_nodes, SCORE, PVAL, block1, block2, blocks, hard_threshold):

            score_cols = SCORE.columns
            score_rows = SCORE.index

            block1_indexes = list(block1_nodes.index)
            block2_indexes = list(block2_nodes.index)

            block1_names = list(block1_nodes['Name'])
            block2_names = list(block2_nodes['Name'])

            block1_nodeColors = list(block1_nodes['Color'].values)
            block2_nodeColors = list(block2_nodes['Color'].values)

            e = []

            for i_idx in range(0, len(score_rows)):

                i = score_rows[i_idx]

                for j_idx in range(i_idx, len(score_cols)):

                    j = score_cols[j_idx]

                    if (abs(SCORE.values[i_idx, j_idx]) > hard_threshold):

                        start_name = block1_names[i_idx]
                        end_name = block2_names[j_idx]

                        start_index = block1_indexes[i_idx]
                        end_index = block2_indexes[j_idx]

                        start_color = block1_nodeColors[i_idx]
                        end_color = block2_nodeColors[j_idx]

                        if start_index != end_index:
                            if PVAL is None:

                                if len(blocks) > 1:
                                    b = [start_index, start_name, start_color, i, block1, end_index, end_name, end_color, j, block2, SCORE.values[i_idx, j_idx], np.sign(SCORE.values[i_idx, j_idx])];
                                else:
                                    b = [start_index, start_name, start_color, i, end_index, end_name, end_color, j, SCORE.values[i_idx, j_idx], np.sign(SCORE.values[i_idx, j_idx])];
                            else:

                                if len(blocks) > 1:
                                    b = [start_index, start_name, start_color, i, block1, end_index, end_name, end_color, j, block2, SCORE.values[i_idx, j_idx], np.sign(SCORE.values[i_idx, j_idx]), PVAL.values[i_idx, j_idx]];
                                else:
                                    b = [start_index, start_name, start_color, i, end_index, end_name, end_color, j, SCORE.values[i_idx, j_idx], np.sign(SCORE.values[i_idx, j_idx]), PVAL.values[i_idx, j_idx]];

                            e.append(b)

            if PVAL is None:

                if len(blocks) > 1:
                    score = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_color', 'start_label', 'start_block', 'end_index', 'end_name', 'end_color', 'end_label', 'end_block', 'Score', 'Sign'])
                else:
                    score = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_color', 'start_label', 'end_index', 'end_name', 'end_color', 'end_label', 'Score', 'Sign'])
            else:

                if len(blocks) > 1:
                    score = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_color', 'start_label', 'start_block', 'end_index', 'end_name', 'end_color', 'end_label', 'end_block', 'Score', 'Sign', 'Pvalue'])
                else:
                    score = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_color', 'start_label', 'end_index', 'end_name', 'end_color', 'end_label', 'Score', 'Sign', 'Pvalue'])

            return score

        def __pval(block1_nodes, block2_nodes, SCORE, PVAL, block1, block2, blocks, hard_threshold):

            score_cols = SCORE.columns
            score_rows = SCORE.index

            block1_indexes = list(block1_nodes.index)
            block2_indexes = list(block2_nodes.index)

            block1_names = list(block1_nodes['Name'])
            block2_names = list(block2_nodes['Name'])

            block1_nodeColors = list(block1_nodes['Color'].values)
            block2_nodeColors = list(block2_nodes['Color'].values)

            e = []

            for i_idx in range(0, len(score_rows)):

                i = score_rows[i_idx]

                for j_idx in range(0, len(score_cols)):

                    j = score_cols[j_idx]

                    start_name = block1_names[i_idx]
                    end_name = block2_names[j_idx]

                    start_index = block1_indexes[i_idx]
                    end_index = block2_indexes[j_idx]

                    start_color = block1_nodeColors[i_idx]
                    end_color = block2_nodeColors[j_idx]

                    if start_index != end_index:
                        if PVAL is None:

                            if len(blocks) > 1:
                                b = [start_index, start_name, start_color, i, block1, end_index, end_name, end_color, j, block2, SCORE.values[i_idx, j_idx], np.sign(SCORE.values[i_idx, j_idx])];
                            else:
                                b = [start_index, start_name, start_color, i, end_index, end_name, end_color, j, SCORE.values[i_idx, j_idx], np.sign(SCORE.values[i_idx, j_idx])];

                            e.append(b)
                        else:
                            if (PVAL.values[i_idx, j_idx] < hard_threshold):

                                if len(blocks) > 1:
                                    b = [start_index, start_name, start_color, i, block1, end_index, end_name, end_color, j, block2, SCORE.values[i_idx, j_idx], np.sign(SCORE.values[i_idx, j_idx]), PVAL.values[i_idx, j_idx]];
                                else:
                                    b = [start_index, start_name, start_color, i, end_index, end_name, end_color, j, SCORE.values[i_idx, j_idx], np.sign(SCORE.values[i_idx, j_idx]), PVAL.values[i_idx, j_idx]];

                                e.append(b)

            if PVAL is None:

                if len(blocks) > 1:
                    pval = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_color', 'start_label', 'start_block', 'end_index', 'end_name', 'end_color', 'end_label', 'end_block', 'Score', 'Sign'])
                else:
                    pval = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_color', 'start_label', 'end_index', 'end_name', 'end_color', 'end_label', 'Score', 'Sign'])
            else:

                if len(blocks) > 1:
                    pval = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_color', 'start_label', 'start_block', 'end_index', 'end_name', 'end_color', 'end_label', 'end_block', 'Score', 'Sign', 'Pvalue'])
                else:
                    pval = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_color', 'start_label', 'end_index', 'end_name', 'end_color', 'end_label', 'Score', 'Sign', 'Pvalue'])

            return pval

        options = {'Score': __score(block1_nodes, block2_nodes, SCORE, PVAL, block1, block2, blocks, hard_threshold), 'Pvalue': __pval(block1_nodes, block2_nodes, SCORE, PVAL, block1, block2, blocks, hard_threshold)}

        edges = pd.DataFrame()

        if filterScoreType in options:
            edges = options[filterScoreType];
        else:
            print ("Error: wrong score type specified. Valid entries are 'Score' and 'Pvalue'.")

        if sign.lower() == "pos":
            edges = edges[edges['Sign'] > 0].reset_index(drop=True)
        elif sign.lower() == "neg":
            edges = edges[edges['Sign'] < 0].reset_index(drop=True)

        return edges

    def __setNodes(self, nodes):

        self.__nodes = nodes

    def __setEdges(self, edges):

        self.__edges = edges