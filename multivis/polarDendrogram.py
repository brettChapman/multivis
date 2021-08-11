import sys
import copy
import string
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from .utils import *
import numpy as np
import pandas as pd

class polarDendrogram:
    usage = """Produces a polar dendrogram given a cartesian dendrogram and generates feature plots of each cluster

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

            plotClusters : Aggregates peaks from each cluster of the polar dendrogram and generates different feature plots across the group/class variables.
                plot_type: The type of plot. Either "point", "violin", "box", "swarm", "violin-swarm" or "box-swarm" (default: 'point')
                column_numbers: The number of columns to display in the plots (default: 4)
                log_data: Perform a log ('natural', base 2 or base 10) on all data (default: (True, 2))
                scale_data: Scale the data ('standard' (centers and scales to unit variance), 'minmax' (scales between 0 and 1), 'maxabs' (scales to the absolute maximum value), 'robust' (centers and scales to between 25th and 75th quantile range) (default: (True, 'minmax'))
                impute_data: Impute any missing values using KNN impute with a set number of nearest neighbours (default: (True, 3))
                figSize: The figure size as a tuple (width,height) (default: (15,10))
                fontSize: The font size for all text (default: 12)
                colour_palette: The colour palette to use for the plot (default: None)
                y_axis_label: The label to customise the y axis (default: None)
                x_axis_rotation: Rotate the x axis labels this number of degrees (default: 0)
                point_estimator: The statistical function to use for the point plot. Either "mean" or "median" (default: 'mean')
                point_ci: The bootstrapped confidence interval for the point plot. Can also be standard deviation ("sd") (default: 95)
                violin_distribution_type: The representation of the distribution of data points within the violin plot. Either "quartile", "box", "point", "stick" or None (default: 'quartile')
                violin_width_scale: The method used to scale the width of the violin plot. Either "area", "count" or "width" (default: "width")
                box_iqr: The proportion past the lower and upper quartiles to extend the plot whiskers for the box plot. Points outside this range will be identified as outliers (default: 1.5)
                saveImage: Setting to 'True' will save the image to file (default: True)
                imageFileName: The image file name to save to (default: [plot_type]_clusters.png')                
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

    def plotClusters(self, plot_type='point', column_numbers=4, log_data=(True, 2), scale_data=(True, 'minmax'), impute_data=(True, 3), figSize=(15, 10), fontSize=12, colour_palette=None, y_axis_label=None, x_axis_rotation=0, point_estimator='mean', point_ci=95, violin_distribution_type='box', violin_width_scale='width', box_iqr=1.5, saveImage=True, imageFileName='_clusters.png', dpi=200):

        cmap_list = list(matplotlib.cm.cmaps_listed) + list(matplotlib.cm.datad)
        cmap_list_r = [cmap + '_r' for cmap in cmap_list]
        cmap_list = cmap_list + cmap_list_r

        dendrogram = self.__dn
        peaktable = self.__peaktable
        datatable = self.__datatable
        group_column_name = self.__group_column_name
        style = self.__style
        transparent = self.__transparent

        plot_types = ["point", "violin", "box", "swarm", "violin-swarm", "box-swarm"]
        estimator_types = ['mean', 'median']

        if plot_type.lower() not in plot_types:
            print("Error: The chosen plot type is invalid. Choose one of \"{}\".".format('\" or \"'.join(plot_types)))
            sys.exit()

        if point_estimator.lower() not in estimator_types:
            print("Error: The chosen point plot estimator is invalid. Choose one of \"{}\".".format('\" or \"'.join(estimator_types)))
            sys.exit()

        if isinstance(point_ci, str):
            if point_ci != 'sd':
                print("Error: The string value for point plot ci is invalid. Choose a float, integer or 'sd' value for standard deviation.")
                sys.exit()
        else:
            if not isinstance(point_ci, float):
                if not isinstance(point_ci, int):
                    print("Error: The value for point plot ci is invalid. Choose a float, integer or 'sd' value for standard deviation.")
                    sys.exit()

        if y_axis_label is not None:
            if not isinstance(y_axis_label, str):
                print("Error: The y axis label is not valid. Use a string value or set to None.")
                sys.exit()

        if colour_palette is not None:
            if not isinstance(colour_palette, str):
                print("Error: Colour palette choice is not valid. Choose a string value.")
                sys.exit()
            else:
                if colour_palette not in cmap_list:
                    print("Error: Colour palette is not valid. Choose one of the following: {}.".format(', '.join(cmap_list)))
                    sys.exit()

        if not isinstance(log_data, tuple):
            print("Error: Log data type if not a tuple. Please ensure the value is a tuple (e.g. (True, 2).")
            sys.exit()
        else:
            (log_bool, log_base) = log_data

            if not isinstance(log_bool, bool):
                print("Error: Log data first tuple item is not a boolean value. Choose either \"True\" or \"False\".")
                sys.exit()

            base_types = ['natural', 2, 10]

            if isinstance(log_base, str):
                log_base = log_base.lower()

            if log_base not in base_types:
                print("Error: Log data second tuple item is not valid. Choose one of {}.".format(', '.join(base_types)))
                sys.exit()

        if not isinstance(scale_data, tuple):
            print("Error: Scale data type if not a tuple. Please ensure the value is a tuple (e.g. (True, 'standard').")
            sys.exit()
        else:
            (scale_bool, scale_type) = scale_data

            if not isinstance(scale_bool, bool):
                print("Error: Scale data first tuple item is not a boolean value. Choose either \"True\" or \"False\".")
                sys.exit()

            scale_types = ['standard', 'minmax', 'maxabs', 'robust']

            if isinstance(scale_type, str):
                scale_type = scale_type.lower()

            if scale_type not in scale_types:
                print("Error: Log data second tuple item is not valid. Choose one of {}.".format(', '.join(scale_types)))
                sys.exit()

        if not isinstance(impute_data, tuple):
            print("Error: Impute data type if not a tuple. Please ensure the value is a tuple (e.g. (True, 3).")
            sys.exit()
        else:
            (impute_bool, k) = impute_data

            if not isinstance(impute_bool, bool):
                print("Error: Impute data first tuple item is not a boolean value. Choose either \"True\" or \"False\".")
                sys.exit()

            if not isinstance(k, float):
                if not isinstance(k, int):
                    print("Error: Impute data second tuple item, the nearest neighbours k value, is not valid. Choose a float or integer value.")
                    sys.exit()

        violin_distribution_types = ['quartile', 'box', 'point', 'stick', None]
        violin_width_scale_types = ['area', 'count', 'width']
        if plot_type.lower() == "violin":
            if violin_distribution_type not in violin_distribution_types:
                print("Error: Violin distribution type not valid. Choose one of the following: {}.".format(', '.join(violin_distribution_types)))
                sys.exit()

            if violin_width_scale not in violin_width_scale_types:
                print("Error: Violin width scale type not valid. Choose one of the following: {}.".format(', '.join(violin_width_scale_types)))
                sys.exit()

        if plot_type.lower == "box":
            if not isinstance(box_iqr, float):
                if not isinstance(box_iqr, int):
                    print("Error: The box plot interquartile range extension beyond whiskers is not valid. Choose a float or integer value.")
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

        (scale_bool, scale_type) = scale_data

        if scale_bool:
            if isinstance(scale_type, str) and scale_type.lower() == 'standard':
                X = scaler(X, type=scale_type.lower()).reset_index(drop=True)
            elif isinstance(scale_type, str) and scale_type.lower() == 'minmax':
                X = scaler(X, type=scale_type.lower()).reset_index(drop=True)
            elif isinstance(scale_type, str) and scale_type.lower() == 'maxabs':
                X = scaler(X, type=scale_type.lower()).reset_index(drop=True)
            elif isinstance(scale_type, str) and scale_type.lower() == 'robust':
                X = scaler(X, type=scale_type.lower()).reset_index(drop=True)
            else:
                print("Error: The chosen scale type is invalid.")
                sys.exit()

        (impute_bool, k) = impute_data;

        if impute_bool:
            X = imputeData(X, k=k).reset_index(drop=True)

        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X, columns=peaklist)

        if peaktable.empty or datatable.empty:
            print("Error: Peak Table and/or Data Table is empty. Can not produce cluster plots. Please provide a populated Data and Peak Table.")
            sys.exit()
        else:
            cluster_palette = self.__get_cluster_palette(dendrogram, peaktable.index)

            ordered_list = dendrogram['ivl']

            clusters = self.__getClusters(ordered_list, cluster_palette)

            with plt.style.context(style):

                fig, axes = plt.subplots(nrows=int(np.ceil(float(len(clusters)/column_numbers))), ncols=column_numbers, sharey=True, figsize=figSize)

                for cluster_index, cluster in enumerate(clusters):

                    peak_cluster = peaktable[peaktable.index.isin(cluster)]

                    x = X[peak_cluster['Name']]

                    df_merged = pd.DataFrame()

                    cluster_names = list(string.ascii_uppercase)

                    peak_count = 0;
                    for index, peak in enumerate(x.columns):

                        peak_count = peak_count + 1;

                        if df_merged.empty:
                            df_merged = pd.merge(datatable.T[~datatable.T.index.isin(peaktable['Name'])].T.reset_index(drop=True), pd.Series(x.values[:, index], name='Aggregated Peaks').reset_index(drop=True), left_index=True, right_index=True)
                        else:
                            df_dat = pd.merge(datatable.T[~datatable.T.index.isin(peaktable['Name'])].T.reset_index(drop=True), pd.Series(x.values[:, index], name='Aggregated Peaks').reset_index(drop=True), left_index=True, right_index=True)
                            df_merged = pd.concat([df_merged, df_dat], axis=0, sort=False).reset_index(drop=True)

                    if plot_type.lower() == 'point':
                        if point_estimator.lower() == 'mean':
                            point_estimator = 'Mean'
                            ax = sns.pointplot(data=df_merged, x=group_column_name, y='Aggregated Peaks', estimator=np.nanmean, capsize=0.1, ci=point_ci, palette=colour_palette, ax=axes.flat[cluster_index])
                        elif point_estimator.lower() == 'median':
                            point_estimator = 'Median'
                            ax = sns.pointplot(data=df_merged, x=group_column_name, y='Aggregated Peaks', estimator=np.nanmedian, capsize=0.1, ci=point_ci, palette=colour_palette, ax=axes.flat[cluster_index])
                        else:
                            print("Error: Invalid point plot estimator type.")
                            sys.exit()

                        ax.tick_params(labelrotation=x_axis_rotation, labelsize=fontSize)

                        if log_bool:
                            if scale_data:
                                if isinstance(point_ci, str):
                                    if point_ci == 'sd':
                                        ax.set_title('Cluster {} (N={}) within SD'.format(cluster_names[cluster_index], peak_count), fontsize=fontSize)
                                        ax.set_xlabel('')
                                        if y_axis_label is None:
                                            ax.set_ylabel('Log({}) scaled ({}) {} Peak Area within SD'.format(log_base, scale_type, point_estimator), fontsize=fontSize)
                                        else:
                                            ax.set_ylabel(y_axis_label, fontsize=fontSize)
                                else:
                                    ax.set_title('Cluster {} (N={}) with {}% CI'.format(cluster_names[cluster_index], peak_count, point_ci), fontsize=fontSize)
                                    ax.set_xlabel('')
                                    if y_axis_label is None:
                                        ax.set_ylabel('Log({}) scaled ({}) {} Peak Area & {}% CI'.format(log_base, scale_type, point_estimator, point_ci), fontsize=fontSize)
                                    else:
                                        ax.set_ylabel(y_axis_label, fontsize=fontSize)
                            else:
                                if isinstance(ci, str):
                                    if ci == 'sd':
                                        ax.set_title('Cluster {} (N={}) within SD'.format(cluster_names[cluster_index], peak_count), fontsize=fontSize)
                                        ax.set_xlabel('')
                                        if y_axis_label is None:
                                            ax.set_ylabel('Log({}) {} Peak Area within SD'.format(log_base, point_estimator), fontsize=fontSize)
                                        else:
                                            ax.set_ylabel(y_axis_label, fontsize=fontSize)
                                else:
                                    ax.set_title('Cluster {} (N={}) with {}% CI'.format(cluster_names[cluster_index], peak_count, point_ci), fontsize=fontSize)
                                    ax.set_xlabel('')
                                    if y_axis_label is None:
                                        ax.set_ylabel('Log({}) {} Peak Area & {}% CI'.format(log_base, point_estimator, point_ci), fontsize=fontSize)
                                    else:
                                        ax.set_ylabel(y_axis_label, fontsize=fontSize)
                        else:
                            if scale_data:
                                if isinstance(point_ci, str):
                                    if point_ci == 'sd':
                                        ax.set_title('Cluster {} (N={}) within SD'.format(cluster_names[cluster_index], peak_count), fontsize=fontSize)
                                        ax.set_xlabel('')
                                        if y_axis_label is None:
                                            ax.set_ylabel('Scaled ({}) {} Peak Area within SD'.format(scale_type, point_estimator), fontsize=fontSize)
                                        else:
                                            ax.set_ylabel(y_axis_label, fontsize=fontSize)
                                else:
                                    ax.set_title('Cluster {} (N={}) with {}% CI'.format(cluster_names[cluster_index], peak_count, point_ci), fontsize=fontSize)
                                    ax.set_xlabel('')
                                    if y_axis_label is None:
                                        ax.set_ylabel('Scaled ({}) {} Peak Area & {}% CI'.format(scale_type, point_estimator, point_ci), fontsize=fontSize)
                                    else:
                                        ax.set_ylabel(y_axis_label, fontsize=fontSize)
                            else:
                                if isinstance(ci, str):
                                    if ci == 'sd':
                                        ax.set_title('Cluster {} (N={}) within SD'.format(cluster_names[cluster_index], peak_count), fontsize=fontSize)
                                        ax.set_xlabel('')
                                        if y_axis_label is None:
                                            ax.set_ylabel('{} Peak Area within SD'.format(point_estimator), fontsize=fontSize)
                                        else:
                                            ax.set_ylabel(y_axis_label, fontsize=fontSize)
                                else:
                                    ax.set_title('Cluster {} (N={}) with {}% CI'.format(cluster_names[cluster_index], peak_count, ci), fontsize=fontSize)
                                    ax.set_xlabel('')
                                    if y_axis_label is None:
                                        ax.set_ylabel('{} Peak Area & {}% CI'.format(point_estimator, point_ci), fontsize=fontSize)
                                    else:
                                        ax.set_ylabel(y_axis_label, fontsize=fontSize)

                    elif plot_type.lower() == 'violin':
                        ax = sns.violinplot(data=df_merged, x=group_column_name, y='Aggregated Peaks', linewidth=1, inner=violin_distribution_type, scale=violin_width_scale, palette=colour_palette, ax=axes.flat[cluster_index])

                        ax.tick_params(labelrotation=x_axis_rotation, labelsize=fontSize)

                        ax.set_title('Cluster {} (N={})'.format(cluster_names[cluster_index], peak_count), fontsize=fontSize)
                        ax.set_xlabel('')

                        if log_bool:
                            if scale_data:
                                if y_axis_label is None:
                                    ax.set_ylabel('Log({}) scaled ({}) Peak Area'.format(log_base, scale_type), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                            else:
                                if y_axis_label is None:
                                    ax.set_ylabel('Log({}) Peak Area'.format(log_base), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                        else:
                            if scale_data:
                                if y_axis_label is None:
                                    ax.set_ylabel('Scaled ({}) Peak Area'.format(scale_type), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                            else:
                                if y_axis_label is None:
                                    ax.set_ylabel('Peak Area', fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)

                    elif plot_type.lower() == 'box':
                        ax = sns.boxplot(data=df_merged, x=group_column_name, y='Aggregated Peaks', palette=colour_palette, whis=box_iqr, ax=axes.flat[cluster_index])

                        ax.tick_params(labelrotation=x_axis_rotation, labelsize=fontSize)

                        ax.set_title('Cluster {} (N={})'.format(cluster_names[cluster_index], peak_count), fontsize=fontSize)
                        ax.set_xlabel('')

                        if log_bool:
                            if scale_data:
                                if y_axis_label is None:
                                    ax.set_ylabel('Log({}) scaled ({}) Peak Area'.format(log_base, scale_type), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                            else:
                                if y_axis_label is None:
                                    ax.set_ylabel('Log({}) Peak Area'.format(log_base), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                        else:
                            if scale_data:
                                if y_axis_label is None:
                                    ax.set_ylabel('Scaled ({}) Peak Area'.format(scale_type), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                            else:
                                if y_axis_label is None:
                                    ax.set_ylabel('Peak Area', fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)

                    elif plot_type.lower() == 'swarm':
                        ax = sns.swarmplot(data=df_merged, x=group_column_name, y='Aggregated Peaks', size=10, palette=colour_palette, ax=axes.flat[cluster_index])

                        ax.tick_params(labelrotation=x_axis_rotation, labelsize=fontSize)

                        ax.set_title('Cluster {} (N={})'.format(cluster_names[cluster_index], peak_count), fontsize=fontSize)
                        ax.set_xlabel('')

                        if log_bool:
                            if scale_data:
                                if y_axis_label is None:
                                    ax.set_ylabel('Log({}) scaled ({}) Peak Area'.format(log_base, scale_type), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                            else:
                                if y_axis_label is None:
                                    ax.set_ylabel('Log({}) Peak Area'.format(log_base), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                        else:
                            if scale_data:
                                if y_axis_label is None:
                                    ax.set_ylabel('Scaled ({}) Peak Area'.format(scale_type), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                            else:
                                if y_axis_label is None:
                                    ax.set_ylabel('Peak Area', fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)

                    elif plot_type.lower() == 'violin-swarm':
                        ax = sns.violinplot(data=df_merged, x=group_column_name, y='Aggregated Peaks', linewidth=1, inner=None, scale=violin_width_scale, palette=colour_palette, ax=axes.flat[cluster_index])
                        ax = sns.swarmplot(data=df_merged, x=group_column_name, y='Aggregated Peaks', color="white", edgecolor="gray", ax=axes.flat[cluster_index])

                        ax.tick_params(labelrotation=x_axis_rotation, labelsize=fontSize)

                        ax.set_title('Cluster {} (N={})'.format(cluster_names[cluster_index], peak_count), fontsize=fontSize)
                        ax.set_xlabel('')

                        if log_bool:
                            if scale_data:
                                if y_axis_label is None:
                                    ax.set_ylabel('Log({}) scaled ({}) Peak Area'.format(log_base, scale_type), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                            else:
                                if y_axis_label is None:
                                    ax.set_ylabel('Log({}) Peak Area'.format(log_base), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                        else:
                            if scale_data:
                                if y_axis_label is None:
                                    ax.set_ylabel('Scaled ({}) Peak Area'.format(scale_type), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                            else:
                                if y_axis_label is None:
                                    ax.set_ylabel('Peak Area', fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)

                    elif plot_type.lower() == 'box-swarm':
                        ax = sns.boxplot(data=df_merged, x=group_column_name, y='Aggregated Peaks', palette=colour_palette, whis=np.inf, ax=axes.flat[cluster_index])
                        ax = sns.swarmplot(data=df_merged, x=group_column_name, y='Aggregated Peaks', color="0.2", ax=axes.flat[cluster_index])

                        ax.tick_params(labelrotation=x_axis_rotation, labelsize=fontSize)

                        ax.set_title('Cluster {} (N={})'.format(cluster_names[cluster_index], peak_count),fontsize=fontSize)
                        ax.set_xlabel('')

                        if log_bool:
                            if scale_data:
                                if y_axis_label is None:
                                    ax.set_ylabel('Log({}) scaled ({}) Peak Area'.format(log_base, scale_type), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                            else:
                                if y_axis_label is None:
                                    ax.set_ylabel('Log({}) Peak Area'.format(log_base), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                        else:
                            if scale_data:
                                if y_axis_label is None:
                                    ax.set_ylabel('Scaled ({}) Peak Area'.format(scale_type), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                            else:
                                if y_axis_label is None:
                                    ax.set_ylabel('Peak Area', fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)

                fig.tight_layout(h_pad=5, w_pad=2)

                if saveImage:
                    plt.savefig(plot_type + 'Plot' + imageFileName, dpi=dpi, transparent=transparent)

                plt.show()

    def __checkDendrogram(self, dn):

        if not isinstance(dn, dict):
            print("Error: A dendrogram dictionary was not entered. Please check your data.")
            sys.exit()

        cluster_color_list = []
        color_list = np.array(list(dn['color_list']))
        for x in color_list:
            if x != 'C0':
                cluster_color_list.append(x)

        first_color = cluster_color_list[0]
        change = False
        for x in cluster_color_list:
            if first_color == x:
                if change:
                    color_cycled = True
                else:
                    color_cycled = False
            else:
                change = True

        if color_cycled:
            print("Error: The set colour palette for the dendrogram repeats. This will introduce errors with peak area plots further in the workflow, so please ensure a broad enough colour palette to cover each cluster or adjust the colour threshold when generating the cartesian dendrogram.")
            sys.exit()

        return dn

    def __paramCheck(self, imageFileName, saveImage, branch_scale, gap, grid, style, transparent, dpi, figSize, fontSize, PeakTable, DataTable, group_column_name, textColorScale, text_color_column, label_column, text_cmap):

        cmap_list = list(matplotlib.cm.cmaps_listed) + list(matplotlib.cm.datad)
        cmap_list_r = [cmap + '_r' for cmap in cmap_list]
        cmap_list = cmap_list + cmap_list_r

        if not isinstance(imageFileName, str):
            print("Error: Image file name is not valid. Choose a string value.")
            sys.exit()

        if not isinstance(saveImage, bool):
            print("Error: Save image is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if branch_scale.lower() not in ["linear", "log", "square"]:
            print("Error: Branch scale not valid. Choose either \"linear\", \"log\" or \"square\".")
            sys.exit()

        if not isinstance(gap, float):
            if not isinstance(gap, int):
                print("Error: Gap is not valid. Choose a float or integer value.")
                sys.exit()

        if not isinstance(grid, bool):
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

        if not isinstance(transparent, bool):
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
        scaled_colors = transform(x, self.__textColorScale, 0, 1)

        return cmap(scaled_colors)

    def __get_cluster_palette(self, dn, labels, label='ivl'):
        cluster_idxs = defaultdict(list)
        for c, pi in zip(dn['color_list'], dn['icoord']):
            for leg in pi[1:3]:
                i = (leg - 5.0) / 10.0
                #Keep clusters if below a certain icoord value and remove any non-clusters (i.e. assigned C0 colour)
                if ((abs(i - int(i)) < 1e-5) and (c != 'C0')):
                    cluster_idxs[c].append(int(i))

        cluster_classes = dict({})
        for c, l in cluster_idxs.items():
            i_l = [dn[label][i] for i in l]
            cluster_classes[c] = i_l

        cluster_palette = dict({})
        for i in list(labels):
            for j in cluster_classes.keys():
                if i in cluster_classes[j]:
                    cluster_palette[i] = j

        return cluster_palette

    def __getClusters(self, ordered_list, col_palette):

        cluster_dict = {}
        for idx, (key, value) in enumerate(col_palette.items()):
            if value in cluster_dict:
                cluster_dict[value].append(key)
            else:
                cluster_dict[value] = [key]

        clusters = list(cluster_dict.values())

        ordered_clusters = []
        cluster_order = []
        for cluster_value in ordered_list:
            for idx, sub_cluster in enumerate(clusters):
                if cluster_value in sub_cluster:
                    if idx not in cluster_order:
                        ordered_clusters.append(sub_cluster)
                        cluster_order.append(idx)

        return ordered_clusters