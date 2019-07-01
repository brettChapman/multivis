import sys
import seaborn as sns
import scipy.spatial as sp, scipy.cluster.hierarchy as hc
from scipy.cluster.hierarchy import dendrogram
from collections import defaultdict
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np
import pandas as pd

class clustermap:

    def __init__(self, matrix, row_linkage, col_linkage):

        matrix, row_linkage, col_linkage = self.__checkData(matrix, row_linkage, col_linkage)

        self.__matrix = matrix;
        self.__row_linkage = row_linkage;
        self.__col_linkage = col_linkage;

        self.set_params()
        self.__set_heatmap_params(xLabels=list(matrix.columns), yLabels=list(matrix.index))
        self.__set_cluster_params()

    def __checkData(self, matrix, row_linkage, col_linkage):

        if not isinstance(matrix, pd.DataFrame):
            print("Error: A dataframe matrix was not entered. Please check your data.")
            sys.exit()

        matrix_row, matrix_col = matrix.shape

        row_count = len(row_linkage) + 1

        col_count = len(col_linkage) + 1

        if matrix_row != row_count:
            print("Error: Matrix row count does not match expected row linkage count. Please check your data.")
            sys.exit()

        if matrix_col != col_count:
            print("Error: Matrix column count does not match expected column linkage count. Please check your data.")
            sys.exit()

        return matrix, row_linkage, col_linkage

    def set_params(self, imageFileName='clusterMap.png', saveImage=True, dpi=200, figSize=(80, 70), dendrogram_ratio_shift=0.0, fontSize=30, heatmap_params={}, cluster_params={}):

        if heatmap_params:
            self.__set_heatmap_params(**heatmap_params)

        if cluster_params:
            self.__set_cluster_params(**cluster_params)

        imageFileName, saveImage, dpi, figSize, dendrogram_ratio_shift, fontSize = self.__paramCheck(imageFileName, saveImage, dpi, figSize, dendrogram_ratio_shift, fontSize)

        self.__imageFileName = imageFileName;
        self.__saveImage = saveImage;
        self.__dpi = dpi;
        self.__figSize = figSize;
        self.__dendrogram_ratio_shift = dendrogram_ratio_shift;
        self.__fontSize = fontSize;

    def __set_heatmap_params(self, xLabels, yLabels, heatmap_cmap='RdYlGn'):

        xLabels, yLabels, heatmap_cmap = self.__heatmap_paramCheck(xLabels, yLabels, heatmap_cmap)

        matrix = self.__matrix

        col_label_dict = dict(zip(list(matrix.columns), xLabels))
        row_label_dict = dict(zip(list(matrix.index), yLabels))

        matrix.rename(columns=col_label_dict, index=row_label_dict, inplace=True)

        self.__matrix = matrix;
        self.__heatmap_cmap = heatmap_cmap;

    def __set_cluster_params(self, cluster_cmap='Set1', rowColorCluster=False, colColorCluster=False, row_color_threshold=10, col_color_threshold=10):

        cluster_cmap, rowColorCluster, colColorCluster, row_color_threshold, col_color_threshold = self.__cluster_paramCheck(cluster_cmap, rowColorCluster, colColorCluster, row_color_threshold, col_color_threshold)

        self.__cluster_cmap = cluster_cmap;
        self.__rowColorCluster = rowColorCluster;
        self.__colColorCluster = colColorCluster;
        self.__row_color_threshold = row_color_threshold;
        self.__col_color_threshold = col_color_threshold;

    def __paramCheck(self, imageFileName, saveImage, dpi, figSize, dendrogram_ratio_shift, fontSize):

        if not isinstance(imageFileName, str):
            print("Error: Image file name is not valid. Choose a string value.")
            sys.exit()

        if not type(saveImage) == bool:
            print("Error: Save image is not valid. Choose either \"True\" or \"False\".")

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
                        print("Error: Figure size value is not valid. Choose a float or integer value.")
                        sys.exit()

        if not isinstance(dendrogram_ratio_shift, float):
            if not isinstance(dendrogram_ratio_shift, int):
                print("Error: Dendrogram ratio shift is not valid. Choose a float or integer value.")
                sys.exit()

        if not isinstance(fontSize, float):
            if not isinstance(fontSize, int):
                print("Error: Font size is not valid. Choose a float or integer value.")
                sys.exit()

        return imageFileName, saveImage, dpi, figSize, dendrogram_ratio_shift, fontSize

    def __heatmap_paramCheck(self, xLabels, yLabels, heatmap_cmap):

        matrix = self.__matrix

        matrix_row, matrix_col = matrix.shape

        if not isinstance(xLabels, list):
            print("Error: XLabels is not valid. Use a list.")
        else:
            if matrix_col != len(xLabels):
                print("Error: XLabels length does not match the matrix column length. Please check your data.")
                sys.exit()

        if not isinstance(yLabels, list):
            print("Error: YLabels is not valid. Use a list.")
            sys.exit()
        else:
            if matrix_row != len(yLabels):
                print("Error: YLabels length does not match the matrix row length. Please check your data.")
                sys.exit()

        if not isinstance(heatmap_cmap, str):
            print("Error: Heatmap CMAP choice is not valid. Choose a string value.")
            sys.exit()
        else:
            cmap_list = matplotlib.cm.cmap_d.keys()

            if heatmap_cmap not in cmap_list:
                print("Error: Heatmap CMAP is not valid. Choose one of the following: {}.".format(', '.join(cmap_list)))
                sys.exit()

        return xLabels, yLabels, heatmap_cmap

    def __cluster_paramCheck(self, cluster_cmap, rowColorCluster, colColorCluster, row_color_threshold, col_color_threshold):

        if not isinstance(cluster_cmap, str):
            print("Error: Cluster CMAP choice is not valid. Choose a string value.")
            sys.exit()
        else:
            cmap_list = matplotlib.cm.cmap_d.keys()

            if cluster_cmap not in cmap_list:
                print("Error: Cluster CMAP is not valid. Choose one of the following: {}.".format(', '.join(cmap_list)))
                sys.exit()

        if not type(rowColorCluster) == bool:
            print("Error: Row colour cluster is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not type(colColorCluster) == bool:
            print("Error: Column colour cluster is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(row_color_threshold, float):
            if not isinstance(row_color_threshold, int):
                print("Error: Row colour threshold is not valid. Choose a float or integer value.")
                sys.exit()

        if not isinstance(col_color_threshold, float):
            if not isinstance(col_color_threshold, int):
                print("Error: Column colour threshold is not valid. Choose a float or integer value.")
                sys.exit()

        return cluster_cmap, rowColorCluster, colColorCluster, row_color_threshold, col_color_threshold

    def __get_cluster_classes(self, dn, labels, label='ivl'):
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

    def run(self):

        matrix = self.__matrix
        row_linkage = self.__row_linkage
        col_linkage = self.__col_linkage
        imageFileName = self.__imageFileName
        saveImage = self.__saveImage
        dpi = self.__dpi
        figSize = self.__figSize
        rowColorCluster = self.__rowColorCluster
        colColorCluster = self.__colColorCluster
        heatmap_cmap = self.__heatmap_cmap
        cluster_cmap = self.__cluster_cmap
        row_color_threshold = self.__row_color_threshold
        col_color_threshold = self.__col_color_threshold
        dendrogram_ratio_shift = self.__dendrogram_ratio_shift
        fontSize = self.__fontSize

        wspace = 0.0025
        colorBar_thickness = 0.01

        clusterCmap = plt.cm.get_cmap(cluster_cmap);

        print(plt.cm.cmap_d.keys())

        clusterColors = []
        for i in range(clusterCmap.N):
            clusterColors.append(matplotlib.colors.rgb2hex(clusterCmap(i)[:3]))

        if rowColorCluster or colColorCluster:

            if rowColorCluster and colColorCluster:

                hc.set_link_color_palette(clusterColors)

                dn = dendrogram(col_linkage, labels=matrix.columns, no_plot=True, color_threshold=col_color_threshold)

                col_colors = self.__get_cluster_classes(dn, matrix.columns)
                col_palette = dict(zip(matrix.columns.unique(), col_colors))

                if list(matrix.index) != list(matrix.columns):
                    clusterColors = [x for x in clusterColors if x not in col_colors]
                    hc.set_link_color_palette(clusterColors)

                dn = dendrogram(row_linkage, labels=matrix.index, no_plot=True, color_threshold=row_color_threshold)

                row_colors = self.__get_cluster_classes(dn, matrix.index)
                row_palette = dict(zip(matrix.index.unique(), row_colors))

                if np.nan not in row_colors:
                    if np.nan not in col_colors:
                        grid = sns.clustermap(matrix.astype(float)
                                              , row_linkage=row_linkage
                                              , col_linkage=col_linkage
                                              , figsize=figSize
                                              , col_colors=col_colors
                                              , row_colors=row_colors
                                              , robust=True
                                              , xticklabels=matrix.columns
                                              , yticklabels=matrix.index
                                              , cmap=heatmap_cmap)

                        plt.setp(grid.ax_heatmap.yaxis.get_majorticklabels(), fontsize=fontSize)
                        plt.setp(grid.ax_heatmap.xaxis.get_majorticklabels(), fontsize=fontSize, rotation=90)

                        hm = grid.ax_heatmap.get_position()
                        col = grid.ax_col_dendrogram.get_position()
                        row = grid.ax_row_dendrogram.get_position()

                        #Set up row colour dendrogram positions
                        grid.ax_row_dendrogram.set_position([row.x0, row.y0, row.width + dendrogram_ratio_shift, row.height])

                        row = grid.ax_row_dendrogram.get_position()

                        grid.ax_row_colors.set_position([row.x1 + wspace, row.y0, colorBar_thickness, row.height])

                        grid.ax_heatmap.set_position([row.x1 + wspace + colorBar_thickness + wspace, hm.y0, hm.width - dendrogram_ratio_shift, hm.height])
                        grid.ax_col_dendrogram.set_position([row.x1 + wspace + colorBar_thickness + wspace, col.y0, col.width - dendrogram_ratio_shift, col.height + dendrogram_ratio_shift])

                        # Set up column colour dendrogram positions
                        hm = grid.ax_heatmap.get_position()
                        col = grid.ax_col_dendrogram.get_position()

                        grid.ax_col_colors.set_position([hm.x0, hm.y1 + wspace, hm.width, colorBar_thickness])

                        grid.ax_col_dendrogram.set_position([col.x0, hm.y1 + wspace + colorBar_thickness + wspace, col.width, col.height])

                        for tick_label in grid.ax_heatmap.axes.get_xticklabels():
                            tick_text = tick_label.get_text()
                            tick_color = col_palette[tick_text]
                            tick_label.set_color(tick_color)

                        for tick_label in grid.ax_heatmap.axes.get_yticklabels():
                            tick_text = tick_label.get_text()
                            tick_color = row_palette[tick_text]
                            tick_label.set_color(tick_color)

                        row = grid.ax_row_dendrogram.get_position()

                        grid.cax.set_position([row.x0 - colorBar_thickness, row.y0, colorBar_thickness, row.height])
                        grid.cax.yaxis.set_ticks_position("left")

                        plt.setp(grid.cax.yaxis.get_majorticklabels(), fontsize=fontSize)
                        plt.setp(grid.cax.xaxis.get_majorticklabels(), fontsize=fontSize)

                        if saveImage:
                            grid.savefig(imageFileName, dpi=dpi)

                    else:
                        print("Too few colours in colour map. Please choose alternative cluster colour map or colour by row only.")
                else:
                    print("Too few colours in colour map. Please choose alternative cluster colour map or colour by column only.")

            elif rowColorCluster:

                hc.set_link_color_palette(clusterColors)

                dn = dendrogram(row_linkage, labels=matrix.index, no_plot=True, color_threshold=row_color_threshold)

                row_colors = self.__get_cluster_classes(dn, matrix.index)
                row_palette = dict(zip(matrix.index.unique(), row_colors))

                if np.nan not in row_colors:
                    grid = sns.clustermap(matrix.astype(float)
                                          , row_linkage=row_linkage
                                          , col_linkage=col_linkage
                                          , figsize=figSize
                                          , row_colors=row_colors
                                          , robust=True
                                          , xticklabels=matrix.columns
                                          , yticklabels=matrix.index
                                          , cmap=heatmap_cmap)

                    plt.setp(grid.ax_heatmap.yaxis.get_majorticklabels(), fontsize=fontSize)
                    plt.setp(grid.ax_heatmap.xaxis.get_majorticklabels(), fontsize=fontSize, rotation=90)

                    # Set up row colour dendrogram positions
                    hm = grid.ax_heatmap.get_position()
                    col = grid.ax_col_dendrogram.get_position()
                    row = grid.ax_row_dendrogram.get_position()

                    grid.ax_row_dendrogram.set_position([row.x0, row.y0, row.width + dendrogram_ratio_shift, row.height])

                    row = grid.ax_row_dendrogram.get_position()

                    grid.ax_row_colors.set_position([row.x1 + wspace, row.y0, colorBar_thickness, row.height])

                    grid.ax_heatmap.set_position([row.x1 + wspace + colorBar_thickness + wspace, hm.y0, hm.width - dendrogram_ratio_shift, hm.height])
                    grid.ax_col_dendrogram.set_position([row.x1 + wspace + colorBar_thickness + wspace, col.y0, col.width - dendrogram_ratio_shift, col.height + dendrogram_ratio_shift])

                    for tick_label in grid.ax_heatmap.axes.get_yticklabels():
                        tick_text = tick_label.get_text()
                        tick_color = row_palette[tick_text]
                        tick_label.set_color(tick_color)

                    row = grid.ax_row_dendrogram.get_position()

                    grid.cax.set_position([row.x0 - colorBar_thickness, row.y0, colorBar_thickness, row.height])
                    grid.cax.yaxis.set_ticks_position("left")

                    plt.setp(grid.cax.yaxis.get_majorticklabels(), fontsize=fontSize)
                    plt.setp(grid.cax.xaxis.get_majorticklabels(), fontsize=fontSize)

                    if saveImage:
                        grid.savefig(imageFileName, dpi=dpi)

                else:
                    print("Error: Too few colours in colour map. Please choose alternative cluster colour map or colour by column only.")
                    sys.exit()

            elif colColorCluster:

                hc.set_link_color_palette(clusterColors)

                dn = dendrogram(col_linkage, labels=matrix.columns, no_plot=True, color_threshold=col_color_threshold)

                col_colors = self.__get_cluster_classes(dn, matrix.columns)
                col_palette = dict(zip(matrix.columns.unique(), col_colors))

                if np.nan not in col_colors:
                    grid = sns.clustermap(matrix.astype(float)
                                          , row_linkage=row_linkage
                                          , col_linkage=col_linkage
                                          , figsize=figSize
                                          , col_colors=col_colors
                                          , robust=True
                                          , xticklabels=matrix.columns
                                          , yticklabels=matrix.index
                                          , cmap=heatmap_cmap)

                    plt.setp(grid.ax_heatmap.yaxis.get_majorticklabels(), fontsize=fontSize)
                    plt.setp(grid.ax_heatmap.xaxis.get_majorticklabels(), fontsize=fontSize, rotation=90)

                    hm = grid.ax_heatmap.get_position()
                    col = grid.ax_col_dendrogram.get_position()
                    row = grid.ax_row_dendrogram.get_position()

                    # Set up column colour dendrogram positions
                    grid.ax_row_dendrogram.set_position([row.x0, row.y0, row.width + dendrogram_ratio_shift, row.height])

                    row = grid.ax_row_dendrogram.get_position()

                    grid.ax_heatmap.set_position([row.x1 + wspace, hm.y0, hm.width - dendrogram_ratio_shift, hm.height])

                    hm = grid.ax_heatmap.get_position()

                    grid.ax_col_colors.set_position([hm.x0, hm.y1 + wspace, hm.width, colorBar_thickness])

                    grid.ax_col_dendrogram.set_position([hm.x0, hm.y1 + wspace + colorBar_thickness + wspace, hm.width, col.height + dendrogram_ratio_shift])

                    for tick_label in grid.ax_heatmap.axes.get_xticklabels():
                        tick_text = tick_label.get_text()
                        tick_color = col_palette[tick_text]
                        tick_label.set_color(tick_color)

                    row = grid.ax_row_dendrogram.get_position()

                    grid.cax.set_position([row.x0 - colorBar_thickness, row.y0, colorBar_thickness, row.height])
                    grid.cax.yaxis.set_ticks_position("left")

                    plt.setp(grid.cax.yaxis.get_majorticklabels(), fontsize=fontSize)
                    plt.setp(grid.cax.xaxis.get_majorticklabels(), fontsize=fontSize)

                    if saveImage:
                        grid.savefig(imageFileName, dpi=dpi)

                else:
                    print("Error: Too few colors in color map. Please choose alternative group colour map or colour by row only.")
                    sys.exit()
        else:

            grid = sns.clustermap(X.astype(float)
                                  , row_linkage=row_linkage
                                  , col_linkage=col_linkage
                                  , figsize=figSize
                                  , robust=True
                                  , xticklabels=matrix.columns
                                  , yticklabels=matrix.index
                                  , cmap=heatmap_cmap)

            plt.setp(grid.ax_heatmap.yaxis.get_majorticklabels(), fontsize=fontSize)
            plt.setp(grid.ax_heatmap.xaxis.get_majorticklabels(), fontsize=fontSize, rotation=90)

            hm = grid.ax_heatmap.get_position()
            col = grid.ax_col_dendrogram.get_position()
            row = grid.ax_row_dendrogram.get_position()

            grid.ax_row_dendrogram.set_position([row.x0, row.y0, row.width + dendrogram_ratio_shift, row.height])

            row = grid.ax_row_dendrogram.get_position()

            grid.ax_heatmap.set_position([row.x1 + wspace, hm.y0, hm.width - dendrogram_ratio_shift, hm.height])
            grid.ax_col_dendrogram.set_position([row.x1 + wspace, col.y0, col.width - dendrogram_ratio_shift, col.height + dendrogram_ratio_shift])

            row = grid.ax_row_dendrogram.get_position()

            grid.cax.set_position([row.x0 - colorBar_thickness, row.y0, colorBar_thickness, row.height])
            grid.cax.yaxis.set_ticks_position("left")

            plt.setp(grid.cax.yaxis.get_majorticklabels(), fontsize=fontSize)
            plt.setp(grid.cax.xaxis.get_majorticklabels(), fontsize=fontSize)

            if saveImage:
                grid.savefig(imageFileName, dpi=dpi)