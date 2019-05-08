import seaborn as sns
import scipy.spatial as sp, scipy.cluster.hierarchy as hc
from scipy.cluster.hierarchy import dendrogram
from collections import defaultdict
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def get_cluster_classes(dn, labels, label='ivl'):
    cluster_idxs = defaultdict(list)
    for c, pi in zip(dn['color_list'], dn['icoord']):
        for leg in pi[1:3]:
            i = (leg - 5.0) / 10.0
            if abs(i - int(i)) < 1e-5:
                cluster_idxs[c].append(int(i))

    cluster_classes = {}
    for c, l in cluster_idxs.items():
        i_l = [dn[label][i] for i in l]
        cluster_classes[c] = i_l

    cluster = []
    for i in labels:
        included = False
        for j in cluster_classes.keys():
            if i in cluster_classes[j]:
                cluster.append(j)
                included = True
        if not included:
            cluster.append(None)

    return cluster

def clustermap(X, row_linkage, col_linkage, imageFileName, rowColorGrouping, colColorGrouping, heatmap_cmap, group_cmap, row_color_threshold, col_color_threshold, fontSize, saveImage, figSize):

    groupCmap = plt.cm.get_cmap(group_cmap);

    groupColors = []
    for i in range(groupCmap.N):
        groupColors.append(matplotlib.colors.rgb2hex(groupCmap(i)[:3]))

    sns.set_context("notebook", font_scale=fontSize)

    if rowColorGrouping or colColorGrouping:

        if rowColorGrouping and colColorGrouping:

            #row_palette = dict(zip(X.index.unique(), groupColors))

            #row_colors = X.index.map(row_palette)

            #g = sns.clustermap(X.astype(float), robust=True, row_linkage=row_linkage, col_linkage=col_linkage)

            hc.set_link_color_palette(groupColors)

            dn = dendrogram(col_linkage, labels=X.columns, no_plot=True, color_threshold=col_color_threshold)

            #col_cluster_colors = get_cluster_classes(dn, X.columns)
            col_colors = get_cluster_classes(dn, X.columns)
            col_palette = dict(zip(X.columns.unique(), col_colors))

            groupColors = [x for x in groupColors if x not in col_colors]

            hc.set_link_color_palette(groupColors)

            dn = dendrogram(row_linkage, labels=X.index, no_plot=True, color_threshold=row_color_threshold)

            #row_cluster_colors = get_cluster_classes(dn, X.index)
            row_colors = get_cluster_classes(dn, X.index)
            row_palette = dict(zip(X.index.unique(), row_colors))

            #if list(X.index) != list(X.columns):
            #    groupColors = [x for x in groupColors if x not in list(row_palette.values())]

            #col_palette = dict(zip(X.columns.unique(), groupColors))

            #row_colors = X.index.map(row_cluster_colors)

            #col_colors = X.columns.map(col_cluster_colors)

            if np.nan not in row_colors:
                if np.nan not in col_colors:
                    grid = sns.clustermap(X.astype(float)
                                          , row_linkage=row_linkage
                                          , col_linkage=col_linkage
                                          , figsize=figSize
                                          , col_colors=col_colors
                                          , row_colors=row_colors
                                          , robust=True
                                          , xticklabels=True
                                          , yticklabels=True
                                          , cmap=heatmap_cmap)

                    for tick_label in grid.ax_heatmap.axes.get_xticklabels():
                        tick_text = tick_label.get_text()
                        tick_color = col_palette[tick_text]
                        tick_label.set_color(tick_color)

                    for tick_label in grid.ax_heatmap.axes.get_yticklabels():
                        tick_text = tick_label.get_text()
                        tick_color = row_palette[tick_text]
                        tick_label.set_color(tick_color)

                    grid.cax.set_position([0.05, 0.22, .03, .45])

                    #print(grid.dendrogram_col.linkage)

                    if saveImage:
                        grid.savefig(imageFileName)

                else:
                    print("Too few colors in color map. Please choose alternative group colour map or colour by row only.")
            else:
                print("Too few colors in color map. Please choose alternative group colour map or colour by column only.")

        elif rowColorGrouping:

            hc.set_link_color_palette(groupColors)

            dn = dendrogram(row_linkage, labels=X.index, no_plot=True, color_threshold=row_color_threshold)

            # row_cluster_colors = get_cluster_classes(dn, X.index)
            row_colors = get_cluster_classes(dn, X.index)
            row_palette = dict(zip(X.index.unique(), row_colors))
            #print(row_palette)

            #row_colors = X.index.map(row_palette)

            if np.nan not in row_colors:
                grid = sns.clustermap(X.astype(float)
                                      , row_linkage=row_linkage
                                      , col_linkage=col_linkage
                                      , figsize=figSize
                                      , row_colors=row_colors
                                      , robust=True
                                      , xticklabels=True
                                      , yticklabels=True
                                      , cmap=heatmap_cmap)

                for tick_label in grid.ax_heatmap.axes.get_yticklabels():
                    tick_text = tick_label.get_text()
                    tick_color = row_palette[tick_text]
                    tick_label.set_color(tick_color)

                grid.cax.set_position([0.05, 0.22, .03, .45])

                if saveImage:
                    grid.savefig(imageFileName)

            else:
                print("Too few colors in color map. Please choose alternative group colour map or colour by column only.")

        elif colColorGrouping:

            hc.set_link_color_palette(groupColors)

            dn = dendrogram(col_linkage, labels=X.columns, no_plot=True, color_threshold=col_color_threshold)

            # row_cluster_colors = get_cluster_classes(dn, X.index)
            col_colors = get_cluster_classes(dn, X.columns)
            col_palette = dict(zip(X.columns.unique(), col_colors))

            if np.nan not in col_colors:
                grid = sns.clustermap(X.astype(float)
                                      , row_linkage=row_linkage
                                      , col_linkage=col_linkage
                                      , figsize=figSize
                                      , col_colors=col_colors
                                      , robust=True
                                      , xticklabels=True
                                      , yticklabels=True
                                      , cmap=heatmap_cmap)

                for tick_label in grid.ax_heatmap.axes.get_xticklabels():
                    tick_text = tick_label.get_text()
                    tick_color = col_palette[tick_text]
                    tick_label.set_color(tick_color)

                grid.cax.set_position([0.05, 0.22, .03, .45])

                if saveImage:
                    grid.savefig(imageFileName)

            else:
                print("Too few colors in color map. Please choose alternative group colour map or colour by row only.")
    else:

        grid = sns.clustermap(X.astype(float)
                              , row_linkage=row_linkage
                              , col_linkage=col_linkage
                              , figsize=figSize
                              , robust=True
                              , xticklabels=True
                              , yticklabels=True
                              , cmap=heatmap_cmap)
        
        grid.cax.set_position([0.05, 0.22, .03, .45])
        
        #ax = grid.ax_heatmap
        
        #col_labels = [label.get_text() for label in ax.xaxis.get_ticklabels()]
        #row_labels = [label.get_text() for label in ax.yaxis.get_ticklabels()]

        if saveImage:
            grid.savefig(imageFileName)

    #return col_labels, row_labels #pd.DataFrame(xlabel_texts, columns=['XLabels']), pd.DataFrame(ylabel_texts, columns=['YLabels'])