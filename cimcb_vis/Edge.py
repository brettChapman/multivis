import pandas as pd
import numpy as np
import networkx as nx

class Edge:
    """Class for edgeBundle and base class for network."""

    def __init__(self, peaks, scores, pvalues):

        self.peaks = self.__checkData(peaks);
        self.scores = self.__checkData(scores);
        self.pvalues = self.__checkData(pvalues);

        self.nodes = pd.DataFrame()
        self.edges = pd.DataFrame()
        self.g = nx.Graph()

        self.set_params()

    def run(self):

        self.__edges()

    def set_params(self, filterScoreType='Pval', link_type='Score', internalCorrelation=False, threshold=0.005, sign="BOTH", verbose=0):

        filterScoreType, link_type, internalCorrelation, threshold, sign, verbose = self.__paramCheck(filterScoreType, link_type, internalCorrelation, threshold, sign, verbose)

        self.filterScoreType = filterScoreType;
        self.link_type = link_type;
        self.internalCorrelation = internalCorrelation;
        self.threshold = threshold;
        self.sign = sign;
        self.verbose = verbose;

    def __checkData(self, DF):

        if not isinstance(DF, pd.DataFrame):
            raise ValueError("A dataframe was not entered. Please check your data.")

        return DF

    def __paramCheck(self, filtScoreType, link_type, internalCorrelation, threshold, sign, verbose):

        if filtScoreType not in ["Pval", "Score"]:
            raise ValueError("Filter score type not valid. Choose either \"Pval\" or \"Score\".")

        if link_type not in ["Pval", "Score"]:
            raise ValueError("Link type not valid. Choose either \"Pval\" or \"Score\".")

        if not type(internalCorrelation) == bool:
            raise ValueError("Internal correlation not valid. Choose either \"True\" or \"False\".")

        if not isinstance(threshold, float):
            if not isinstance(threshold, int):
                raise ValueError("Threshold is not valid. Choose a float or integer value.")

        if sign not in ["POS", "NEG", "BOTH"]:
            raise ValueError("Sign is not valid. Choose either \"POS\" or \"NEG\" or \"BOTH\".")

        if verbose not in [0, 1]:
            raise ValueError("Verbose not valid. Choose either 0 or 1.")

        return filtScoreType, link_type, internalCorrelation, threshold, sign, verbose

    def __scoreBlock1(self, nodes, peaks, scores, pvalues, blocks, block1):

        if len(blocks) > 1:
            block1_labels = list(peaks[peaks['Block'] == block1]['Label'].values)
            block1_names = list(peaks[peaks['Block'] == block1]['Name'].values)
            block1_colors = list(peaks[peaks['Block'] == block1]['Color'].values)
        else:
            block1_labels = list(peaks['Label'].values)
            block1_names = list(peaks['Name'].values)
            block1_colors = list(peaks['Color'].values)

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
            nodes = pd.DataFrame(np.column_stack([block1_labels, block1_names, block1_colors]), columns=['label', 'name', 'color'])
            nodes['group'] = block1
        else:
            addedBlocks = list(np.unique(nodes['group'].values))

            if block1 not in addedBlocks:
                dat = pd.DataFrame(np.column_stack([block1_labels, block1_names, block1_colors, block1_node_size]), columns=['label', 'name', 'color'])
                dat['group'] = block1

                nodes = pd.concat([nodes, dat], sort=False).reset_index(drop=True)

        if not len(blocks) > 1:
            nodes = nodes.drop(columns="group")

        return nodes, scoreBlocks_blocked1, pvalBlocks_blocked1, block1_labels

    def __scoreBlock2(self, nodes, peaks, scoreBlocks_blocked1, pvalBlocks_blocked1, blocks, block2, block1_labels):

        if len(blocks) > 1:
            block2_labels = list(peaks[peaks['Block'] == block2]['Label'].values)
            block2_names = list(peaks[peaks['Block'] == block2]['Name'].values)
            block2_colors = list(peaks[peaks['Block'] == block2]['Color'].values)
        else:
            block2_labels = list(peaks['Label'].values)
            block2_names = list(peaks['Name'].values)
            block2_colors = list(peaks['Color'].values)

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
            nodes = pd.DataFrame(np.column_stack([block2_labels, block2_names, block2_colors]), columns=['label', 'name', 'color'])
            nodes['group'] = block2
        else:
            addedBlocks = list(np.unique(nodes['group'].values))

            if block2 not in addedBlocks:
                dat = pd.DataFrame(np.column_stack([block2_labels, block2_names, block2_colors]), columns=['label', 'name', 'color'])
                dat['group'] = block2

                nodes = pd.concat([nodes, dat], sort=False).reset_index(drop=True)

        return nodes, scoreBlocks_blocked2, pvalBlocks_blocked2

    def __buildEdges(self, nodes, SCORE, PVAL, block1, block2, filtScoreType, threshold, sign):

        if 'group' in nodes.columns:
            blocks = list(nodes['group'].unique())
        else:
            blocks = [1]

        if len(blocks) > 1:
            block1_nodes = nodes[nodes['group'] == block1]
            block2_nodes = nodes[nodes['group'] == block2]
        else:
            block1_nodes = nodes
            block2_nodes = nodes

        def __score(block1_nodes, block2_nodes, SCORE, PVAL, block1, block2, blocks, threshold):

            score_cols = SCORE.columns
            score_rows = SCORE.index

            block1_indexes = list(block1_nodes.index)
            block2_indexes = list(block2_nodes.index)

            block1_names = list(block1_nodes['name'])
            block2_names = list(block2_nodes['name'])

            block1_nodeColors = list(block1_nodes['color'].values)
            block2_nodeColors = list(block2_nodes['color'].values)

            e = []

            for i_idx in range(0, len(score_rows)):

                i = score_rows[i_idx]

                for j_idx in range(i_idx, len(score_cols)):

                    j = score_cols[j_idx]

                    if (abs(SCORE.values[i_idx, j_idx]) > threshold):

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
                    score = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_color', 'start_label', 'start_block', 'end_index', 'end_name', 'end_color', 'end_label', 'end_block', 'Score', 'Sign', 'Pval'])
                else:
                    score = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_color', 'start_label', 'end_index', 'end_name', 'end_color', 'end_label', 'Score', 'Sign', 'Pval'])

            return score

        def __pval(block1_nodes, block2_nodes, SCORE, PVAL, block1, block2, blocks, threshold):

            score_cols = SCORE.columns
            score_rows = SCORE.index

            block1_indexes = list(block1_nodes.index)
            block2_indexes = list(block2_nodes.index)

            block1_names = list(block1_nodes['name'])
            block2_names = list(block2_nodes['name'])

            block1_nodeColors = list(block1_nodes['color'].values)
            block2_nodeColors = list(block2_nodes['color'].values)

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
                            if (PVAL.values[i_idx, j_idx] < threshold):

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
                    pval = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_color', 'start_label', 'start_block', 'end_index', 'end_name', 'end_color', 'end_label', 'end_block', 'Score', 'Sign', 'Pval'])
                else:
                    pval = pd.DataFrame(e, columns=['start_index', 'start_name', 'start_color', 'start_label', 'end_index', 'end_name', 'end_color', 'end_label', 'Score', 'Sign', 'Pval'])

            return pval

        options = {'Score': __score(block1_nodes, block2_nodes, SCORE, PVAL, block1, block2, blocks, threshold), 'Pval': __pval(block1_nodes, block2_nodes, SCORE, PVAL, block1, block2, blocks, threshold)}

        edges = pd.DataFrame()

        if filtScoreType in options:
            edges = options[filtScoreType];
        else:
            print ("Error: wrong score type specified. Valid entries are 'Score' and 'Pval'.")

        if sign == "POS":
            edges = edges[edges['Sign'] > 0].reset_index(drop=True)
        elif sign == "NEG":
            edges = edges[edges['Sign'] < 0].reset_index(drop=True)

        return edges

    def __edges(self):

        peaks = self.peaks
        scores = self.scores
        pvalues = self.pvalues

        filterScoreType = self.filterScoreType
        threshold = self.threshold
        sign = self.sign

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

                if self.internalCorrelation:

                    nodes, scoreBlocks_blocked2, pvalBlocks_blocked2 = self.__scoreBlock2(nodes, peaks, scoreBlocks_blocked1, pvalBlocks_blocked1, blocks, block2, block1_labels);

                    if edges.empty:
                        edges = self.__buildEdges(nodes, scoreBlocks_blocked2, pvalBlocks_blocked2, block1, block2, filterScoreType, threshold, sign)
                    else:
                        dat_edges = self.__buildEdges(nodes, scoreBlocks_blocked2, pvalBlocks_blocked2, block1, block2, filterScoreType, threshold, sign)
                        edges = pd.concat([edges, dat_edges], sort=False).reset_index(drop=True)
                else:

                    if block1 != block2:

                        nodes, scoreBlocks_blocked2, pvalBlocks_blocked2 = self.__scoreBlock2(nodes, peaks, scoreBlocks_blocked1, pvalBlocks_blocked1, blocks, block2, block1_labels);

                        if edges.empty:
                            edges = self.__buildEdges(nodes, scoreBlocks_blocked2, pvalBlocks_blocked2, block1, block2, filterScoreType, threshold, sign)
                        else:
                            dat_edges = self.__buildEdges(nodes, scoreBlocks_blocked2, pvalBlocks_blocked2, block1, block2, filterScoreType, threshold, sign)
                            edges = pd.concat([edges, dat_edges], sort=False).reset_index(drop=True)
                    else:
                        if len(blocks) == 1:
                            edges = self.__buildEdges(nodes, scoreBlocks_blocked1, pvalBlocks_blocked1, block1, block2, filterScoreType, threshold, sign)

        self.nodes = nodes
        self.edges = edges
        self.g = self.__networkXEdges(nodes, edges)

    def __networkXEdges(self, nodes, edges):

        if 'group' in nodes.columns:
            blocks = list(nodes['group'].unique())
        else:
            blocks = [1]

        g = nx.Graph()

        for idx, indexName in enumerate(nodes.index):

            if 'group' in nodes.columns:
                g.add_node(indexName, label=nodes['label'].values[idx]
                       , name=nodes['name'].values[idx]
                       , group=nodes['group'].values[idx]
                       , color=nodes['color'].values[idx])
            else:
                g.add_node(indexName, label=nodes['label'].values[idx]
                           , name=nodes['name'].values[idx]
                           , color=nodes['color'].values[idx])

        if "Pval" in edges.columns:

            if len(blocks) > 1:
                for source_index, _, _, source, source_block, target_index, _, _, target, target_block, score, pval, _ in edges.values:

                    if self.link_type == "Pval":
                        g.add_edge(source_index, target_index, weight=pval)
                    elif self.link_type == "Score":
                        g.add_edge(source_index, target_index, weight=score)
            else:
                for source_index, _, _, source, target_index, _, _, target, score, pval, _ in edges.values:

                    if self.link_type == "Pval":
                        g.add_edge(source_index, target_index, weight=pval)
                    elif self.link_type == "Score":
                        g.add_edge(source_index, target_index, weight=score)
        else:
            if len(blocks) > 1:
                for source_index, _, _, source, source_block, target_index, _, _, target, target_block, score, _ in edges.values:
                    g.add_edge(source_index, target_index, weight=score)
            else:
                for source_index, _, _, source, target_index, _, _, target, score, _ in edges.values:
                    g.add_edge(source_index, target_index, weight=score)

        return g

    def getNodes(self):

        return self.nodes

    def getEdges(self):

        return self.edges

    def getNetworkx(self):

        return self.g

    def getLinkType(self):

        return self.link_type
