import sys
import copy
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from .utils import *
import numpy as np
import pandas as pd

class polarDendrogram:
    usage = """Produces a polar dendrogram given a cartesian dendrogram

            Initial_Parameters
            ----------
            dn :  Dendrogram dictionary labelled by Peak Table index.

            Methods
            -------
            set_params : Set parameters -
                imageFileName: The image file name to save to (default: 'polarDendrogram.png')
                saveImage: Setting to 'True' will save the image to file (default: True)
                branch_scale: The branch distance scale to apply ('linear', 'log', 'square') (default: 'linear')
                gap: The gap size within the polar dendrogram (default: 0.1)
                grid: Setting to 'True' will overlay a grid over the polar dendrogram (default: False)
                style: Set the matplotlib style (see https://matplotlib.org/stable/tutorials/introductory/customizing.html) (default: 'seaborn-white')
                transparent: Setting to 'True' will make the background of all plots transparent (default: False)
                dpi: The number of Dots Per Inch (DPI) for the image (default: 200)
                figSize: The figure size as a tuple (width,height) (default: (10,10))
                fontSize: The font size for all text (default: 15)
                PeakTable: The Peak Table Pandas dataframe (default: empty dataframe)
                DataTable: The Data Table Pandas dataframe (default: empty dataframe)
                group_column_name: The group column name used in the datatable (e.g. 'Class') (default: None)
                textColorScale: The scale to use for colouring the text ("linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume", "ordinal", "reverse_ordinal") (default: 'linear')
                text_color_column: The colour column to use from Peak Table (default: None sets to black)
                label_column: The label column to use from Peak Table (default: use original Peak Table index from cartesian dendrogram)
                text_cmap: The CMAP colour palette to use (default: 'brg')

            getClusterPlots : Generates plots of mean/median peak area over the group/class variable for each cluster from the polar dendrogram
                plot_type: The type of plot to plot. Either mean peak area or median peak area (default: 'mean')
                column_numbers: The number of columns to display in the plots (default: 4)
                log_data: Perform a log ('natural', base 2 or base 10) on all data (default: (True, 2))
                scale_data: Scale the data to unit variance (default: True)
                impute_data: Impute any missing values using KNN impute with a set number of nearest neighbours (default: (True, 3))
                figSize: The figure size as a tuple (width,height) (default: (15,10))
                x_axis_rotation: Rotate the x axis labels this number of degrees (default: 0)
                ci: The bootstrapped confidence interval. Can also be standard deviation ("sd") (default: 95)
                saveImage: Setting to 'True' will save the image to file (default: True)
                imageFileName: The image file name to save to (default: 'clusterPlots.png')                
                dpi: The number of Dots Per Inch (DPI) for the image (default: 200)
            
            help : Print this help text

            build : Generates and displays the Polar dendrogram.
    """

    def __init__(self, dn):

        self.__dn = self.__checkDendrogram(dn)

        self.set_params()

    def help(self):
        print(polarDendrogram.usage)

    def set_params(self, imageFileName='polarDendrogram.png', saveImage=True, branch_scale='linear', gap=0.1, grid=False, style='seaborn-white', transparent=False, dpi=200, figSize=(10,10), fontSize=15, PeakTable=pd.DataFrame(), DataTable=pd.DataFrame(), group_column_name=None, textColorScale='linear', text_color_column='none', label_column='none', text_cmap='brg'):

        imageFileName, saveImage, branch_scale, gap, grid, style, transparent, dpi, figSize, fontSize, PeakTable, DataTable, group_column_name, textColorScale, text_color_column, label_column, text_cmap = self.__paramCheck(imageFileName, saveImage, branch_scale, gap, grid, style, transparent, dpi, figSize, fontSize, PeakTable, DataTable, group_column_name, textColorScale, text_color_column, label_column, text_cmap)

        self.__imageFileName = imageFileName;
        self.__saveImage = saveImage;
        self.__branch_scale = branch_scale;
        self.__gap = gap;
        self.__grid = grid;
        self.__style = style;
        self.__transparent = transparent;
        self.__dpi = dpi;
        self.__figSize = figSize;
        self.__fontSize = fontSize;
        self.__peaktable = PeakTable;
        self.__datatable = DataTable;
        self.__group_column_name = group_column_name;
        self.__textColorScale = textColorScale;
        self.__text_color_column = text_color_column;
        self.__label_column = label_column;
        self.__text_cmap = text_cmap;

    def __process_params(self):

        peaktable = self.__peaktable
        text_cmap = self.__text_cmap
        text_color_column = self.__text_color_column
        label_column = self.__label_column

        if peaktable.empty:
            text_colors = dict({})
            labels = dict({})
        else:
            textCmap = plt.cm.get_cmap(text_cmap)  # Sets the color palette for the text

            if text_color_column == 'none':
                text_colors = {}
            else:
                colorsHEX = []

                text_color_values = peaktable[text_color_column].values

                try:
                    float(text_color_values[0])

                    text_color_values = np.array([float(i) for i in text_color_values])

                    colorsRGB = self.__get_colors(text_color_values, textCmap)[:, :3]

                    for rgb in colorsRGB:
                        colorsHEX.append(matplotlib.colors.rgb2hex(rgb))

                    text_colors = dict(zip(peaktable.index, colorsHEX))
                except ValueError:
                    if matplotlib.colors.is_color_like(text_color_values[0]):
                        text_colors = dict(zip(peaktable.index, text_color_values))
                    else:
                        if ((self.__textColorScale != "ordinal") and (self.__textColorScale != "reverse_ordinal")):
                            print("Error: Text colour column is not valid. While textColorScale is not ordinal or reverse_ordinal, choose a column containing colour values (names, hex code or RGB values), floats or integer values.")
                            sys.exit()
                        else:
                            colorsRGB = self.__get_colors(text_color_values, textCmap)[:, :3]

                            for rgb in colorsRGB:
                                colorsHEX.append(matplotlib.colors.rgb2hex(rgb))

                            text_colors = dict(zip(peaktable.index, colorsHEX))

            if label_column == 'none':
                labels = dict({})
            else:
                labels = dict(zip(peaktable.index, peaktable[label_column]))

        return text_colors, labels

    def build(self):

        imageFileName = self.__imageFileName
        saveImage = self.__saveImage
        dendrogram = self.__dn
        branch_scale = self.__branch_scale
        gap = self.__gap
        grid = self.__grid
        fontSize = self.__fontSize
        style = self.__style
        transparent = self.__transparent
        dpi = self.__dpi
        figSize = self.__figSize

        text_colors, labels = self.__process_params()

        icoord = np.array(dendrogram['icoord'], dtype=float)
        dcoord = np.array(dendrogram['dcoord'], dtype=float)
        idx_labels = np.array(dendrogram['ivl'])
        colors = np.array(dendrogram['color_list'])

        if branch_scale.lower() == "log":
            dcoord = -np.log(dcoord + 1)
        elif branch_scale.lower() == "square":
            dcoord = -np.square(dcoord + 1)
        elif branch_scale.lower() == "linear":
            dcoord = -np.array(dcoord + 1)

        imax = icoord.max()
        imin = icoord.min()

        icoord = ((icoord - imin) / (imax - imin) * (1 - gap) + gap / 2) * 2 * np.pi

        with plt.style.context(style):
            fig = plt.figure(figsize=figSize)
            ax = fig.add_subplot(111, polar=True)

            # ax.set_rmax(2)
            # ax.set_rlabel_position(0)

            angleRange = []
            for xs, ys, c in zip(icoord, dcoord, colors):
                xs = self.__smoothsegment(xs)
                ys = self.__smoothsegment(ys)

                angleRange.extend(xs)

                ax.plot(xs, ys, color=c)

            ax.spines['polar'].set_visible(False)
            ax.set_yticklabels([])

            iimin = np.array(angleRange).min()
            iimax = np.array(angleRange).max()

            Nxticks = len(idx_labels)

            angles = np.linspace(iimin, iimax, Nxticks)

            xticks = copy.deepcopy(angles)

            angles[np.cos(angles) < 0] = angles[np.cos(angles) < 0] + np.pi

            angles = np.rad2deg(angles)

            ax.set_xticks(xticks)
            ax.set_xticklabels(idx_labels)

            fig.canvas.draw()

            xlabels = []
            for label, theta, angle in zip(ax.get_xticklabels(), angles, np.rad2deg(xticks)):
                x, y = label.get_position()

                if angle <= 90:
                    ha = 'left'
                elif angle <= 270:
                    ha = 'right'
                else:
                    ha = 'left'

                if labels and text_colors:
                    lab = ax.text(x, y + 0.05, labels[int(label.get_text())],
                                  color=text_colors[int(label.get_text())], fontsize=fontSize, rotation=theta,
                                  transform=label.get_transform(), rotation_mode="anchor", ha=ha, va="center")
                elif not labels and not text_colors:
                    lab = ax.text(x, y + 0.05, label.get_text(), color="black", fontsize=fontSize, rotation=theta,
                                  transform=label.get_transform(), rotation_mode="anchor", ha=ha, va="center")
                elif labels:
                    lab = ax.text(x, y + 0.05, labels[int(label.get_text())], color="black", fontsize=fontSize,
                                  rotation=theta, transform=label.get_transform(), rotation_mode="anchor", ha=ha,
                                  va="center")
                elif text_colors:
                    lab = ax.text(x, y + 0.05, label.get_text(), color=text_colors[int(label.get_text())],
                                  fontsize=fontSize, rotation=theta, transform=label.get_transform(),
                                  rotation_mode="anchor", ha=ha, va="center")

                xlabels.append(lab)

            ax.set_xticklabels([])

            ax.grid(grid)

            ax.patch.set_alpha(1.0)

            if saveImage:
                plt.savefig(imageFileName, dpi=dpi, transparent=transparent);

            plt.show()

    def getClusterPlots(self, plot_type='mean', column_numbers=4, log_data=(True, 2), scale_data=True, impute_data=(True, 3), figSize=(15, 10), x_axis_rotation=0, ci=95, saveImage=True, imageFileName='clusterPlots.png', dpi=200):

        dendrogram = self.__dn
        peaktable = self.__peaktable
        datatable = self.__datatable
        group_column_name = self.__group_column_name
        style = self.__style
        transparent = self.__transparent

        plot_types = ['mean', 'median']

        if plot_type.lower() not in plot_types:
            print("Error: The chosen plot type is invalid. Choose one of \"{}\".".format('\" or \"'.join(plot_types)))
            sys.exit()

        if isinstance(ci, str):
            if ci != 'sd':
                print("Error: The string value for ci is invalid. Choose a float, integer or 'sd' value for standard deviation.")
                sys.exit()
        else:
            if not isinstance(ci, float):
                if not isinstance(ci, int):
                    print("Error: The value for 'ci' is not valid. Choose a float, integer or 'sd' value for standard deviation.")
                    sys.exit()

        peaklist = peaktable['Name']
        X = datatable[peaklist]

        (log_bool, log_base) = log_data;

        if log_bool:
            if isinstance(log_base, str) and log_base.lower() == 'natural':
                X = X.applymap(np.log);
            elif log_base == 2:
                X = X.applymap(np.log2);
            elif log_base == 10:
                X = X.applymap(np.log10);
            else:
                print("Error: The chosen log type is invalid.")
                sys.exit()

        if scale_data:
            X = scaler(X, "standard")

        (impute_bool, k) = impute_data;

        if impute_bool:
            X = imputeData(X, k=k)

        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X, columns=peaklist)

        if peaktable.empty or datatable.empty:
            print("Error: Peak Table and/or Data Table is empty. Can not produce cluster plots. Please provide a populated Data and Peak Table.")
            sys.exit()
        else:
            col_colors = self.__get_cluster_classes(dendrogram, peaktable.index)

            col_palette = dict(zip(peaktable.index.unique(), col_colors))

            ordered_list = dendrogram['ivl']

            clusters = self.__getClusters(ordered_list, col_palette)

            with plt.style.context(style):

                fig, axes = plt.subplots(nrows=int(np.ceil(float(len(clusters)/column_numbers))), ncols=column_numbers, sharey=True, figsize=figSize)

                for cluster_index, cluster in enumerate(clusters):

                    peak_cluster = peaktable[peaktable.index.isin(cluster)]

                    x = X[peak_cluster['Name']]

                    df_merged = pd.DataFrame()

                    cluster_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
                                     'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

                    peak_count = 0;
                    for index, peak in enumerate(x.columns):

                        peak_count = peak_count + 1;

                        if df_merged.empty:
                            df_merged = pd.merge(datatable.T[~datatable.T.index.isin(peaktable['Name'])].T.reset_index(drop=True), pd.Series(x.values[:, index], name='Peak').reset_index(drop=True), left_index=True, right_index=True)
                        else:
                            df_dat = pd.merge(datatable.T[~datatable.T.index.isin(peaktable['Name'])].T.reset_index(drop=True), pd.Series(x.values[:, index], name='Peak').reset_index(drop=True), left_index=True, right_index=True)
                            df_merged = pd.concat([df_merged, df_dat], axis=0, sort=False).reset_index(drop=True)

                    if plot_type == 'mean':
                        ax = sns.pointplot(data=df_merged, x=group_column_name, y='Peak', x_estimator=np.nanmean, capsize=0.1, ci=ci, ax=axes.flat[cluster_index])
                    elif plot_type == 'median':
                        ax = sns.pointplot(data=df_merged, x=group_column_name, y='Peak', x_estimator=np.nanmedian, capsize=0.1, ci=ci, ax=axes.flat[cluster_index])
                    else:
                        print("Error: Invalid plot type.")
                        sys.exit()

                    ax.tick_params(labelrotation=x_axis_rotation)

                    if log_bool:
                        if scale_data:
                            if isinstance(ci, str):
                                if ci == 'sd':
                                    ax.set(xlabel='', ylabel='Log({}) scaled (unit variance) Peak Area within SD'.format(log_base), title='Cluster {} (N={}) within SD'.format(cluster_names[cluster_index], peak_count))
                            else:
                                ax.set(xlabel='', ylabel='Log({}) scaled (unit variance) Peak Area & {}% CI'.format(log_base, ci), title='Cluster {} (N={}) with {}% CI'.format(cluster_names[cluster_index], peak_count, ci))
                        else:
                            if isinstance(ci, str):
                                if ci == 'sd':
                                    ax.set(xlabel='', ylabel='Log({}) Peak Area within SD'.format(log_base), title='Cluster {} (N={}) within SD'.format(cluster_names[cluster_index], peak_count))
                            else:
                                ax.set(xlabel='', ylabel='Log({}) Peak Area & {}% CI'.format(log_base, ci), title='Cluster {} (N={}) with {}% CI'.format(cluster_names[cluster_index], peak_count, ci))
                    else:
                        if scale_data:
                            if isinstance(ci, str):
                                if ci == 'sd':
                                    ax.set(xlabel='', ylabel='Scaled (unit variance) Peak Area within SD', title='Cluster {} (N={}) within SD'.format(cluster_names[cluster_index], peak_count))
                            else:
                                ax.set(xlabel='', ylabel='Scaled (unit variance) Peak Area & {}% CI'.format(ci), title='Cluster {} (N={}) with {}% CI'.format(cluster_names[cluster_index], peak_count, ci))
                        else:
                            if isinstance(ci, str):
                                if ci == 'sd':
                                    ax.set(xlabel='', ylabel='Peak Area within SD', title='Cluster {} (N={}) within SD'.format(cluster_names[cluster_index], peak_count))
                            else:
                                ax.set(xlabel='', ylabel='Peak Area & {}% CI'.format(ci), title='Cluster {} (N={}) with {}% CI'.format(cluster_names[cluster_index], peak_count, ci))


                fig.tight_layout(h_pad=5, w_pad=2)

                if saveImage:
                    plt.savefig(imageFileName, dpi=dpi, transparent=transparent)

                plt.show()

    def __checkDendrogram(self, dn):

        if not isinstance(dn, dict):
            print("Error: A dendrogram dictionary was not entered. Please check your data.")
            sys.exit()

        return dn

    def __paramCheck(self, imageFileName, saveImage, branch_scale, gap, grid, style, transparent, dpi, figSize, fontSize, PeakTable, DataTable, group_column_name, textColorScale, text_color_column, label_column, text_cmap):

        cmap_list = list(matplotlib.cm.cmaps_listed) + list(matplotlib.cm.datad)
        cmap_list_r = [cmap + '_r' for cmap in cmap_list]
        cmap_list = cmap_list + cmap_list_r

        if not isinstance(imageFileName, str):
            print("Error: Image file name is not valid. Choose a string value.")
            sys.exit()

        if not type(saveImage) == bool:
            print("Error: Save image is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if branch_scale.lower() not in ["linear", "log", "square"]:
            print("Error: Branch scale not valid. Choose either \"linear\", \"log\" or \"square\".")
            sys.exit()

        if not isinstance(gap, float):
            if not isinstance(gap, int):
                print("Error: Gap is not valid. Choose a float or integer value.")
                sys.exit()

        if not type(grid) == bool:
            print("Error: Grid is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(style, str):
            print("Error: Seaborn style is not valid. Choose a string value.")
            sys.exit()
        else:
            styleList = list(plt.style.available)

            if style not in styleList:
                print("Error: Chosen style is not valid. Choose one of the following: {}.".format(', '.join(styleList)))
                sys.exit()

        if not type(transparent) == bool:
            print("Error: The transparent value is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

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

        if not isinstance(fontSize, float):
            if not isinstance(fontSize, int):
                print("Error: Font size is not valid. Choose a float or integer value.")
                sys.exit()

        if not isinstance(PeakTable, pd.DataFrame):
            print("Error: Provided Peak Table is not valid. Choose a Pandas dataframe.")
            sys.exit()
        else:
            if not PeakTable.empty:
                if "Name" not in PeakTable.columns:
                    print("Peak Table does not contain the required 'Name' column")
                    sys.exit()

        if not isinstance(DataTable, pd.DataFrame):
            print("Error: Provided Data Table is not valid. Choose a Pandas dataframe.")
            sys.exit()
        else:
            if not DataTable.empty:
                if group_column_name not in DataTable.columns:
                    print("Error: Data Table does not contain the specified group column name {}. Please check your data.".format(''.join(group_column_name)))
                    sys.exit()

        if textColorScale.lower() not in ["linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume", "ordinal", "reverse_ordinal"]:
            print("Error: Node color scale type not valid. Choose either \"linear\", \"reverse_linear\", \"log\", \"reverse_log\", \"square\", \"reverse_square\", \"area\", \"reverse_area\", \"volume\", \"reverse_volume\", \"ordinal\", \"reverse_ordinal\".")
            sys.exit()

        col_list = list(PeakTable.columns) + ['none']

        if text_color_column not in col_list:
            print("Error: Text color column not valid. Choose one of {}.".format(', '.join(col_list)))
            sys.exit()
        else:
            if text_color_column != 'none':
                text_color_values = np.array(PeakTable[text_color_column].values)

                if ((textColorScale != 'ordinal') and (textColorScale != 'reverse_ordinal')):
                    try:
                        float(text_color_values[0])
                    except ValueError:
                        if not matplotlib.colors.is_color_like(text_color_values[0]):
                            print("Error: Text colour column is not valid. While textColorScale is not ordinal or reverse_ordinal, choose a column containing colour values (names, hex code or RGB values), floats or integer values.")
                            sys.exit()

        if label_column not in col_list:
            print("Error: Label column not valid. Choose one of {}.".format(', '.join(col_list)))
            sys.exit()

        if not isinstance(text_cmap, str):
            print("Error: Text CMAP is not valid. Choose a string value.")
            sys.exit()
        else:
            if text_cmap not in cmap_list:
                print("Error: Text CMAP is not valid. Choose one of the following: {}.".format(', '.join(cmap_list)))
                sys.exit()

        return imageFileName, saveImage, branch_scale, gap, grid, style, transparent, dpi, figSize, fontSize, PeakTable, DataTable, group_column_name, textColorScale, text_color_column, label_column, text_cmap

    def __smoothsegment(self, seg, Nsmooth=100):
        return np.concatenate([[seg[0]], np.linspace(seg[1], seg[2], Nsmooth), [seg[3]]])

    def __get_colors(self, x, cmap):
        scaled_colors = scaleData(x, self.__textColorScale, 0, 1)

        return cmap(scaled_colors)

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

    def __getClusters(self, ordered_list, col_palette):

        clusters = []
        sub_cluster = []
        prev_color = col_palette[ordered_list[0]]

        for index, i in enumerate(ordered_list):
            color = col_palette[i]

            if color == prev_color:
                sub_cluster.append(i)
            else:
                clusters.append(sub_cluster)
                sub_cluster = []
                sub_cluster.append(i)

            if index == len(ordered_list) - 1:
                clusters.append(sub_cluster)

            prev_color = color

        return clusters