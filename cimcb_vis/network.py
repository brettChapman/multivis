import pandas as pd
import numpy as np
#from collections import Counter
#from scipy import stats
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
#from sklearn.preprocessing import normalize
from .utils import *
from .networks import *

def corrBlock1(df_nodes, peaks, corr_blocks, pval_blocks, blocks, block1, groupColors):

    block1_labels = list(peaks[peaks['Block'] == block1]['Label'].values)
    block1_names = list(peaks[peaks['Block'] == block1]['Name'].values)
    block1_colors = list(peaks[peaks['Block'] == block1]['Text_color'].values)
    block1_node_size = list(peaks[peaks['Block'] == block1]['Size'].values)

    if len(blocks) == 1:

        corrBlocks_blocked1 = corr_blocks

        corrBlocks_blocked1.index = block1_labels
        corrBlocks_blocked1.columns = block1_labels
    else:
        corrBlocks_blocked1 = corr_blocks[corr_blocks.index.isin(block1_names)]

    if pval_blocks is not None:
        if len(blocks) == 1:

            pvalBlocks_blocked1 = pval_blocks

            pvalBlocks_blocked1.index = block1_labels
            pvalBlocks_blocked1.columns = block1_labels
        else:
            pvalBlocks_blocked1 = pval_blocks[pval_blocks.index.isin(block1_names)]

    else:
        pvalBlocks_blocked1 = None;

    if df_nodes.empty:
        df_nodes = pd.DataFrame(np.column_stack([block1_labels, block1_names, block1_colors, block1_node_size]), columns=['label', 'name', 'sig_color', 'node_size'])
        df_nodes['group_color'] = groupColors[blocks.index(block1)]
        df_nodes['group'] = block1
    else:
        addedBlocks = list(np.unique(df_nodes['group'].values))

        if block1 not in addedBlocks:
            dat = pd.DataFrame(np.column_stack([block1_labels, block1_names, block1_colors, block1_node_size]), columns=['label', 'name', 'sig_color', 'node_size'])
            dat['group_color'] = groupColors[blocks.index(block1)]
            dat['group'] = block1

            df_nodes = pd.concat([df_nodes, dat], sort=False).reset_index(drop=True)

    return df_nodes, corrBlocks_blocked1, pvalBlocks_blocked1, block1_labels

def corrBlock2(df_nodes, peaks, corrBlocks_blocked1, pvalBlocks_blocked1, blocks, block2, groupColors, block1_labels):

    block2_labels = list(peaks[peaks['Block'] == block2]['Label'].values)
    block2_names = list(peaks[peaks['Block'] == block2]['Name'].values)
    block2_colors = list(peaks[peaks['Block'] == block2]['Text_color'].values)
    block2_node_size = list(peaks[peaks['Block'] == block2]['Size'].values)

    corrBlocks_blocked2 = corrBlocks_blocked1[block2_names].astype(float)

    corrBlocks_blocked2.index = block1_labels
    corrBlocks_blocked2.columns = block2_labels

    if pvalBlocks_blocked1 is not None:
        pvalBlocks_blocked2 = pvalBlocks_blocked1[block2_names].astype(float)
        pvalBlocks_blocked2.index = block1_labels
        pvalBlocks_blocked2.columns = block2_labels
    else:
        pvalBlocks_blocked2 = None;

    if df_nodes.empty:
        df_nodes = pd.DataFrame(np.column_stack([block2_labels, block2_names, block2_colors, block2_node_size]), columns=['label', 'name', 'sig_color', 'node_size'])
        df_nodes['group_color'] = groupColors[blocks.index(block2)]
        df_nodes['group'] = block2
    else:
        addedBlocks = list(np.unique(df_nodes['group'].values))

        if block2 not in addedBlocks:
            dat = pd.DataFrame(np.column_stack([block2_labels, block2_names, block2_colors, block2_node_size]), columns=['label', 'name', 'sig_color', 'node_size'])
            dat['group_color'] = groupColors[blocks.index(block2)]
            dat['group'] = block2

            df_nodes = pd.concat([df_nodes, dat], sort=False).reset_index(drop=True)

    return df_nodes, corrBlocks_blocked2, pvalBlocks_blocked2

def network(multi_peaks, corr_blocks, pval_blocks, filtScoreType, link_type, internalCorrelation, size_column, invertSize, sizeScale, size_range, lengthScale, length_range, level, sign, edge_cmap, group_cmap):

    blocks = list(multi_peaks['Block'].unique())

    edgeCmap = plt.cm.get_cmap(edge_cmap) #Sets the color pallete for the edges
    groupCmap = plt.cm.get_cmap(group_cmap) #Sets the color palette for the different blocks

    groupColors = []
    for i in range(groupCmap.N):
        groupColors.append(matplotlib.colors.rgb2hex(groupCmap(i)[:3]))

    df_nodes = pd.DataFrame();
    df_edges = pd.DataFrame();

    peaks = multi_peaks.assign(Size=multi_peaks[size_column].values)

    if invertSize:
        peaks['Size'] = np.divide(1, list(peaks['Size'].values))

    if sizeScale == 'linear':
        peaks['Size'] = [round(x) for x in list(map(int, range_scale(peaks['Size'].values, size_range[0], size_range[1])))]
    elif sizeScale == 'log':
        peaks['Size']= peaks['Size'].apply(np.log)
        peaks['Size'] = [round(x) for x in list(map(int, range_scale(peaks['Size'].values, size_range[0], size_range[1])))]
    elif sizeScale == 'square':
        peaks['Size'] = peaks['Size'].apply(np.square)
        peaks['Size'] = [round(x) for x in list(map(int, range_scale(peaks['Size'].values, size_range[0], size_range[1])))]
    elif sizeScale == 'area':
        peaks['Size'] = [np.square(x) for x in list(map(float, peaks['Size'].values))]
        peaks['Size'] = [np.multiply(x, np.pi) for x in list(map(float, peaks['Size'].values))]
        peaks['Size'] = [round(x) for x in list(map(int, range_scale(peaks['Size'].values, size_range[0], size_range[1])))]
    elif sizeScale == 'volume':
        peaks['Size'] = [np.power(x, 3) for x in list(map(float, peaks['Size'].values))]
        peaks['Size'] = [np.multiply(x, np.pi) for x in list(map(float, peaks['Size'].values))]
        peaks['Size'] = [np.multiply(x, 4/3) for x in list(map(float, peaks['Size'].values))]
        peaks['Size'] = [round(x) for x in list(map(int, range_scale(peaks['Size'].values, size_range[0], size_range[1])))]

    for idx, block1 in enumerate(blocks):

        df_nodes, corrBlocks_blocked1, pvalBlocks_blocked1, block1_labels = corrBlock1(df_nodes, peaks, corr_blocks, pval_blocks, blocks, block1, groupColors)

        for block2 in blocks[idx:]:

            if pval_blocks is None:
                filtScoreType = 'Rho';

            if internalCorrelation:

                df_nodes, corrBlocks_blocked2, pvalBlocks_blocked2 = corrBlock2(df_nodes, peaks, corrBlocks_blocked1,  pvalBlocks_blocked1, blocks, block2, groupColors, block1_labels);

                if df_edges.empty:
                    df_edges = network_edges_OnPLS(df_nodes, corrBlocks_blocked2, pvalBlocks_blocked2, block1, block2, filtScoreType, level, sign)
                else:
                    dat_edges = network_edges_OnPLS(df_nodes, corrBlocks_blocked2, pvalBlocks_blocked2, block1, block2, filtScoreType, level, sign)
                    df_edges = pd.concat([df_edges, dat_edges], sort=False).reset_index(drop=True)
            else:

                if block1 != block2:

                    df_nodes, corrBlocks_blocked2, pvalBlocks_blocked2 = corrBlock2(df_nodes, peaks, corrBlocks_blocked1, pvalBlocks_blocked1, blocks, block2, groupColors, block1_labels);

                    if df_edges.empty:
                        df_edges = network_edges(df_nodes, corrBlocks_blocked2, pvalBlocks_blocked2, block1, block2, filtScoreType, level, sign)
                    else:
                        dat_edges = network_edges(df_nodes, corrBlocks_blocked2, pvalBlocks_blocked2, block1, block2, filtScoreType, level, sign)
                        df_edges = pd.concat([df_edges, dat_edges], sort=False).reset_index(drop=True)
                else:
                    if len(blocks) == 1:
                        df_edges = network_edges(df_nodes, corrBlocks_blocked1, pvalBlocks_blocked1, block1, block2, filtScoreType, level, sign)

    if pval_blocks is not None:
        df_edges = network_edge_color(df_edges, link_type, edgeCmap)
    else:
        df_edges = network_edge_color(df_edges, 'Rho', edgeCmap)

    g = nx.Graph()

    for idx, indexName in enumerate(df_nodes.index):
        g.add_node(indexName, label=df_nodes['label'].values[idx]
                   , name=df_nodes['name'].values[idx]
                   , group=df_nodes['group'].values[idx]
                   , color=df_nodes['group_color'].values[idx]
                   , size=df_nodes['node_size'].values[idx]
                   , node_x=0
                   , node_y=0)

    if pval_blocks is not None:

        if link_type == "Pval":
            edge_dist = np.array(list(df_edges['Pval'].values))
            edge_dist = [x for x in list(range_scale(edge_dist, 1, 10))]
        elif link_type == "Rho":
            edge_dist = np.array(list(df_edges['Rho'].values))
            edge_dist = [x for x in list(range_scale(edge_dist, 1, 10))]
            edge_dist = np.divide(1, edge_dist)

        if lengthScale == 'linear':
            edge_distance = [x for x in list(range_scale(edge_dist, length_range[0], length_range[1]))]
        elif lengthScale == 'log':
            edge_dist = np.log(edge_dist)
            edge_distance = [x for x in list(range_scale(edge_dist, length_range[0], length_range[1]))]
        elif lengthScale == 'square':
            edge_dist = np.square(edge_dist)
            edge_distance = [x for x in list(range_scale(edge_dist, length_range[0], length_range[1]))]

        df_edges = df_edges.assign(length=edge_distance)

        for source_index, _, source, source_block, target_index, _, target, target_block, rho, pval, _, length in df_edges.values:

            if link_type == "Pval":
                g.add_edge(source_index, target_index, weight=pval, len=length)
            elif link_type == "Rho":
                g.add_edge(source_index, target_index, weight=rho, len=length)
    else:
        edge_dist = np.divide(1, list(df_edges['Rho'].values))

        if lengthScale == 'linear':
            edge_distance = [x for x in list(range_scale(edge_dist, length_range[0], length_range[1]))]
        elif lengthScale == 'log':
            edge_dist = np.log(edge_dist)
            edge_distance = [x for x in list(range_scale(edge_dist, length_range[0], length_range[1]))]
        elif lengthScale == 'square':
            edge_dist = np.square(edge_dist)
            edge_distance = [x for x in list(range_scale(edge_dist, length_range[0], length_range[1]))]

        df_edges = df_edges.assign(length=edge_distance)

        for source_index, _, source, source_block, target_index, _, target, target_block, rho, _, length in df_edges.values:

            g.add_edge(source_index, target_index, weight=rho, len=length)

    return g, df_nodes, df_edges