import sys
import seaborn as sns
import scipy.cluster.hierarchy as hc
from scipy.cluster.hierarchy import dendrogram
from collections import defaultdict
import matplotlib
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import pandas as pd
import copy

class clustermap:
    usage = """Produces a Hierarchical Clustered Heatmap.

        Initial_Parameters
        ----------
        scores : Pandas dataframe containing scores.
        row_linkage : Precomputed linkage matrix for the rows from a linkage clustered distance/similarities matrix
        col_linkage : Precomputed linkage matrix for the columns from a linkage clustered distance/similarities matrix

        Methods
        -------
        set_params : Set parameters -
            xLabels: A Pandas Series for labelling the X axis
            yLabels: A Pandas Series for labelling the Y axis
            imageFileName: The image file name to save to (default: 'clusterMap.png')
            saveImage: Setting to 'True' will save the image to file (default: True)
            dpi: The number of Dots Per Inch (DPI) for the image (default: 200)
            figSize: The figure size as a tuple (width,height) (default: (80,70))
            dendrogram_ratio_shift: The ratio to shift the position of the dendrogram in relation to the heatmap (default: 0.0)
            dendrogram_line_width: The line width of the dendrograms (default: 1.5)
            background_colour: Set the background colour (default: 'white')
            transparent: Setting to 'True' will ignore background_colour and make the background transparent (default: False)
            fontSize: The font size for all text (default: 30)
            heatmap_annotation: Annotate the heatmap with values (default: False)
            heatmap_cmap: The CMAP colour palette to use for the heatmap (default: 'RdYlGn')
            cluster_cmap: The CMAP colour palette to use for the branch separation of clusters in the dendrogram (default: 'Set1')
            rowColorCluster: Setting to 'True' will display a colour bar for the clustered rows (default: False)
            colColorCluster: Setting to 'True' will display a colour bar for the clustered columns (default: False)
            row_color_threshold: The colouring threshold for the row dendrogram (default: 1)
            col_color_threshold: The colouring threshold for the column dendrogram (default: 1)
        
        help : Print this help text

        build : Generates and displays the Hierarchical Clustered Heatmap (HCH).
    """

    def __init__(self, scores, row_linkage, col_linkage):

        scores, row_linkage, col_linkage = self.__checkData(scores, row_linkage, col_linkage)

        self.__original_scores = copy.deepcopy(scores);
        self.__row_linkage = row_linkage;
        self.__col_linkage = col_linkage;

        self.set_params(xLabels=pd.Series(scores.columns), yLabels=pd.Series(scores.index))

    def help(self):
        print(clustermap.usage)

    def set_params(self, xLabels, yLabels, imageFileName='clusterMap.png', saveImage=True, dpi=200, figSize=(80, 70), dendrogram_ratio_shift=0.0, dendrogram_line_width=1.5, background_colour='white', transparent=False, fontSize=30, heatmap_annotation=False, heatmap_cmap='RdYlGn', cluster_cmap='Set1', rowColorCluster=False, colColorCluster=False, row_color_threshold=10, col_color_threshold=10):

        imageFileName, saveImage, dpi, figSize, dendrogram_ratio_shift, dendrogram_line_width, background_colour, transparent, fontSize, heatmap_annotation, xLabels, yLabels, heatmap_cmap, cluster_cmap, rowColorCluster, colColorCluster, row_color_threshold, col_color_threshold = self.__paramCheck(imageFileName, saveImage, dpi, figSize, dendrogram_ratio_shift, dendrogram_line_width, background_colour, transparent, fontSize, heatmap_annotation, xLabels, yLabels, heatmap_cmap, cluster_cmap, rowColorCluster, colColorCluster, row_color_threshold, col_color_threshold)

        scores = self.__original_scores
        xLabels = list(xLabels)
        yLabels = list(yLabels)
        xLabels_c = copy.deepcopy(xLabels)
        yLabels_c = copy.deepcopy(yLabels)

        # Search for duplicate labels and amend with a suffix (for colouring dendrogram)
        xLabel_counts = {k: v for k, v in Counter(list(xLabels_c)).items() if v > 1}
        yLabel_counts = {k: v for k, v in Counter(list(yLabels_c)).items() if v > 1}

        for i in reversed(range(len(list(xLabels_c)))):
            item = str(list(xLabels_c)[i])
            if item in xLabel_counts and xLabel_counts[item]:
                xLabels_c[i] += "_" + str(xLabel_counts[item])
                xLabel_counts[item] -= 1

        for i in reversed(range(len(list(yLabels_c)))):
            item = str(list(yLabels_c)[i])
            if item in yLabel_counts and yLabel_counts[item]:
                yLabels_c[i] += "_" + str(yLabel_counts[item])
                yLabel_counts[item] -= 1

        col_label_dict = dict(zip(list(scores.columns), xLabels_c))
        row_label_dict = dict(zip(list(scores.index), yLabels_c))

        scores.rename(columns=col_label_dict, index=row_label_dict, inplace=True)

        self.__scores = copy.deepcopy(scores);
        self.__imageFileName = imageFileName;
        self.__saveImage = saveImage;
        self.__dpi = dpi;
        self.__figSize = figSize;
        self.__dendrogram_ratio_shift = dendrogram_ratio_shift;
        self.__background_colour = background_colour
        self.__transparent = transparent
        self.__fontSize = fontSize;
        self.__heatmap_annotation = heatmap_annotation;
        self.__dendrogram_line_width = dendrogram_line_width;
        self.__heatmap_cmap = heatmap_cmap;
        self.__cluster_cmap = cluster_cmap;
        self.__rowColorCluster = rowColorCluster;
        self.__colColorCluster = colColorCluster;
        self.__row_color_threshold = row_color_threshold;
        self.__col_color_threshold = col_color_threshold;

    def build(self):

        scores = self.__scores
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
        dendrogram_line_width = self.__dendrogram_line_width
        background_colour = self.__background_colour
        transparent = self.__transparent
        fontSize = self.__fontSize
        heatmap_annotation = self.__heatmap_annotation

        #Set the background colour
        plt.rcParams['figure.facecolor'] = background_colour

        wspace = 0.0025
        colorBar_thickness = 0.01

        clusterCmap = plt.cm.get_cmap(cluster_cmap);

        clusterColors = []
        for i in range(clusterCmap.N):
            clusterColors.append(matplotlib.colors.rgb2hex(clusterCmap(i)[:3]))

        if rowColorCluster or colColorCluster:

            if rowColorCluster and colColorCluster:

                hc.set_link_color_palette(clusterColors)

                try:
                    dn = dendrogram(col_linkage, labels=scores.columns, no_plot=True, color_threshold=col_color_threshold)
                except IndexError:
                    print("Error: Column colour threshold too high. Try a lower value.")
                    sys.exit()

                col_colors = self.__get_cluster_classes(dn, scores.columns)
                col_palette = dict(zip(scores.columns.unique(), col_colors))

                if list(scores.index) != list(scores.columns):
                    clusterColors = [x for x in clusterColors if x not in col_colors]
                    hc.set_link_color_palette(clusterColors)

                try:
                    dn = dendrogram(row_linkage, labels=scores.index, no_plot=True, color_threshold=row_color_threshold)
                except IndexError:
                    print("Error: Row colour threshold too high. Try a lower value.")
                    sys.exit()

                row_colors = self.__get_cluster_classes(dn, scores.index)
                row_palette = dict(zip(scores.index.unique(), row_colors))

                if np.nan not in row_colors:
                    if np.nan not in col_colors:

                        grid = sns.clustermap(scores.astype(float)
                                              , row_linkage=row_linkage
                                              , col_linkage=col_linkage
                                              , figsize=figSize
                                              , col_colors=col_colors
                                              , row_colors=row_colors
                                              , robust=True
                                              , annot=heatmap_annotation
                                              , annot_kws={"fontsize":fontSize*0.50}
                                              , xticklabels=scores.columns
                                              , yticklabels=scores.index
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

                        grid.ax_heatmap.set_xlabel('')
                        grid.ax_heatmap.set_ylabel('')

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

                        for line in grid.ax_row_dendrogram.collections:
                            line.set_linewidth(dendrogram_line_width)

                        for line in grid.ax_col_dendrogram.collections:
                            line.set_linewidth(dendrogram_line_width)

                        if saveImage:
                            grid.savefig(imageFileName, dpi=dpi, transparent=transparent)

                    else:
                        print("Too few colours in colour map. Please choose alternative cluster colour map or colour by row only.")
                else:
                    print("Too few colours in colour map. Please choose alternative cluster colour map or colour by column only.")

            elif rowColorCluster:

                hc.set_link_color_palette(clusterColors)

                try:
                    dn = dendrogram(row_linkage, labels=scores.index, no_plot=True, color_threshold=row_color_threshold)
                except IndexError:
                    print("Error: Row colour threshold too high. Try a lower value.")
                    sys.exit()

                row_colors = self.__get_cluster_classes(dn, scores.index)
                row_palette = dict(zip(scores.index.unique(), row_colors))

                if np.nan not in row_colors:
                    grid = sns.clustermap(scores.astype(float)
                                          , row_linkage=row_linkage
                                          , col_linkage=col_linkage
                                          , figsize=figSize
                                          , row_colors=row_colors
                                          , robust=True
                                          , annot=heatmap_annotation
                                          , xticklabels=scores.columns
                                          , yticklabels=scores.index
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

                    grid.ax_heatmap.set_xlabel('')
                    grid.ax_heatmap.set_ylabel('')

                    for tick_label in grid.ax_heatmap.axes.get_yticklabels():
                        tick_text = tick_label.get_text()
                        tick_color = row_palette[tick_text]
                        tick_label.set_color(tick_color)

                    row = grid.ax_row_dendrogram.get_position()

                    grid.cax.set_position([row.x0 - colorBar_thickness, row.y0, colorBar_thickness, row.height])
                    grid.cax.yaxis.set_ticks_position("left")

                    plt.setp(grid.cax.yaxis.get_majorticklabels(), fontsize=fontSize)
                    plt.setp(grid.cax.xaxis.get_majorticklabels(), fontsize=fontSize)

                    for line in grid.ax_row_dendrogram.collections:
                        line.set_linewidth(dendrogram_line_width)

                    for line in grid.ax_col_dendrogram.collections:
                        line.set_linewidth(dendrogram_line_width)

                    if saveImage:
                        grid.savefig(imageFileName, dpi=dpi, transparent=transparent)

                else:
                    print("Error: Too few colours in colour map. Please choose alternative cluster colour map or colour by column only.")
                    sys.exit()

            elif colColorCluster:

                hc.set_link_color_palette(clusterColors)

                try:
                    dn = dendrogram(col_linkage, labels=scores.columns, no_plot=True, color_threshold=col_color_threshold)
                except IndexError:
                    print("Error: Column colour threshold too high. Try a lower value.")
                    sys.exit()

                col_colors = self.__get_cluster_classes(dn, scores.columns)
                col_palette = dict(zip(scores.columns.unique(), col_colors))

                if np.nan not in col_colors:
                    grid = sns.clustermap(scores.astype(float)
                                          , row_linkage=row_linkage
                                          , col_linkage=col_linkage
                                          , figsize=figSize
                                          , col_colors=col_colors
                                          , robust=True
                                          , annot=heatmap_annotation
                                          , xticklabels=scores.columns
                                          , yticklabels=scores.index
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

                    grid.ax_heatmap.set_xlabel('')
                    grid.ax_heatmap.set_ylabel('')

                    for tick_label in grid.ax_heatmap.axes.get_xticklabels():
                        tick_text = tick_label.get_text()
                        tick_color = col_palette[tick_text]
                        tick_label.set_color(tick_color)

                    row = grid.ax_row_dendrogram.get_position()

                    grid.cax.set_position([row.x0 - colorBar_thickness, row.y0, colorBar_thickness, row.height])
                    grid.cax.yaxis.set_ticks_position("left")

                    plt.setp(grid.cax.yaxis.get_majorticklabels(), fontsize=fontSize)
                    plt.setp(grid.cax.xaxis.get_majorticklabels(), fontsize=fontSize)

                    for line in grid.ax_row_dendrogram.collections:
                        line.set_linewidth(dendrogram_line_width)

                    for line in grid.ax_col_dendrogram.collections:
                        line.set_linewidth(dendrogram_line_width)

                    if saveImage:
                        grid.savefig(imageFileName, dpi=dpi, transparent=transparent)

                else:
                    print("Error: Too few colors in color map. Please choose alternative group colour map or colour by row only.")
                    sys.exit()
        else:

            grid = sns.clustermap(scores.astype(float)
                                  , row_linkage=row_linkage
                                  , col_linkage=col_linkage
                                  , figsize=figSize
                                  , robust=True
                                  , annot=heatmap_annotation
                                  , xticklabels=scores.columns
                                  , yticklabels=scores.index
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

            grid.ax_heatmap.set_xlabel('')
            grid.ax_heatmap.set_ylabel('')

            row = grid.ax_row_dendrogram.get_position()

            grid.cax.set_position([row.x0 - colorBar_thickness, row.y0, colorBar_thickness, row.height])
            grid.cax.yaxis.set_ticks_position("left")

            plt.setp(grid.cax.yaxis.get_majorticklabels(), fontsize=fontSize)
            plt.setp(grid.cax.xaxis.get_majorticklabels(), fontsize=fontSize)

            for line in grid.ax_row_dendrogram.collections:
                line.set_linewidth(dendrogram_line_width)

            for line in grid.ax_col_dendrogram.collections:
                line.set_linewidth(dendrogram_line_width)

            if saveImage:
                grid.savefig(imageFileName, dpi=dpi, transparent=transparent)

    def __checkData(self, scores, row_linkage, col_linkage):

        if not isinstance(scores, pd.DataFrame):
            print("Error: A dataframe was not entered. Please check your data.")
            sys.exit()

        scores_row, scores_col = scores.shape

        row_count = len(row_linkage) + 1

        col_count = len(col_linkage) + 1

        if scores_row != row_count:
            print("Error: Matrix row count does not match expected row linkage count. Please check your data.")
            sys.exit()

        if scores_col != col_count:
            print("Error: Matrix column count does not match expected column linkage count. Please check your data.")
            sys.exit()

        return scores, row_linkage, col_linkage

    def __paramCheck(self, imageFileName, saveImage, dpi, figSize, dendrogram_ratio_shift, dendrogram_line_width, background_colour, transparent, fontSize, heatmap_annotation, xLabels, yLabels, heatmap_cmap, cluster_cmap, rowColorCluster, colColorCluster, row_color_threshold, col_color_threshold):

        cmap_list = list(matplotlib.cm.cmaps_listed) + list(matplotlib.cm.datad)
        cmap_list_r = [cmap + '_r' for cmap in cmap_list]
        cmap_list = cmap_list + cmap_list_r

        if not isinstance(imageFileName, str):
            print("Error: Image file name is not valid. Choose a string value.")
            sys.exit()

        if not isinstance(saveImage, bool):
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

        if not isinstance(dendrogram_line_width, float):
            if not isinstance(dendrogram_line_width, int):
                print("Error: Dendrogram line width is not valid. Choose a float or integer value.")
                sys.exit()

        if not matplotlib.colors.is_color_like(background_colour):
            print("Error: The background colour value is not valid. Choose a valid colour as a HTML/CSS name, hex code, or (R,G,B) tuple.")
            sys.exit()

        if not isinstance(transparent, bool):
            print("Error: The transparent value is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(fontSize, float):
            if not isinstance(fontSize, int):
                print("Error: Font size is not valid. Choose a float or integer value.")
                sys.exit()

        if not isinstance(heatmap_annotation, bool):
            print("Error: The heatmap annotation value is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        scores = self.__original_scores

        scores_row, scores_col = scores.shape

        if not isinstance(xLabels, pd.Series):
            print("Error: XLabels is not valid. Use a Pandas Series.")
        else:
            if scores_col != len(list(xLabels)):
                print("Error: XLabels length does not match the scores column length. Please check your data.")
                sys.exit()

        if not isinstance(yLabels, pd.Series):
            print("Error: YLabels is not valid. Use a Pandas Series.")
            sys.exit()
        else:
            if scores_row != len(list(yLabels)):
                print("Error: YLabels length does not match the scores row length. Please check your data.")
                sys.exit()

        if not isinstance(heatmap_cmap, str):
            print("Error: Heatmap CMAP choice is not valid. Choose a string value.")
            sys.exit()
        else:
            if heatmap_cmap not in cmap_list:
                print("Error: Heatmap CMAP is not valid. Choose one of the following: {}.".format(', '.join(cmap_list)))
                sys.exit()

        if not isinstance(cluster_cmap, str):
            print("Error: Cluster CMAP choice is not valid. Choose a string value.")
            sys.exit()
        else:
            if cluster_cmap not in cmap_list:
                print("Error: Cluster CMAP is not valid. Choose one of the following: {}.".format(', '.join(cmap_list)))
                sys.exit()

        if not isinstance(rowColorCluster, bool):
            print("Error: Row colour cluster is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(colColorCluster, bool):
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

        return imageFileName, saveImage, dpi, figSize, dendrogram_ratio_shift, dendrogram_line_width, background_colour, transparent, fontSize, heatmap_annotation, xLabels, yLabels, heatmap_cmap, cluster_cmap, rowColorCluster, colColorCluster, row_color_threshold, col_color_threshold

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