import sys
import copy
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from .utils import *
import numpy as np
import pandas as pd

class plotFeatures:
    usage = """Produces different feature plots given a data table and peak table.

            Initial_Parameters
            ----------
            peaktable : Pandas dataframe containing peak data. Must contain 'Name' and 'Label'.
            datatable : Pandas dataframe containing matrix of values to plot (N samples x N features). Columns/features must be same as 'Name' from Peak Table.

            Methods
            -------
            set_params : Set parameters -
                plot_type: The type of plot. Either "point", "violin", "box", "swarm", "violin-swarm" or "box-swarm" (default: 'point')
                column_numbers: The number of columns to display in the plots (default: 4)                
                log_data: Perform a log ('natural', base 2 or base 10) on all data (default: (True, 2))
                scale_data: Scale the data ('standard' (centers to the mean and scales to unit variance), 'minmax' (scales between 0 and 1), 'maxabs' (scales to the absolute maximum value), 'robust' (centers to the median and scales to between 25th and 75th quantile range) (default: (True, 'minmax'))
                impute_data: Impute any missing values using KNN impute with a set number of nearest neighbours (default: (True, 3))
                style: Set the matplotlib style (see https://matplotlib.org/stable/tutorials/introductory/customizing.html) (default: 'seaborn-white')
                transparent: Setting to 'True' will make the background transparent (default: False)                
                figSize: The figure size as a tuple (width,height) (default: (15,10))
                fontSize: The font size for all text (default: 12)
                colour_palette: The colour palette to use for the plot (default: None)
                y_axis_label: The label to customise the y axis (default: None)
                x_axis_rotation: Rotate the x axis labels this number of degrees (default: 0)
                group_column_name: The group column name used in the datatable (e.g. 'Class') (default: None)                
                point_estimator: The statistical function to use for the point plot. Either "mean" or "median" (default: 'mean')
                point_ci: The bootstrapped confidence interval for the point plot. Can also be standard deviation ("sd") (default: 95)
                violin_distribution_type: The representation of the distribution of data points within the violin plot. Either "quartile", "box", "point", "stick" or None (default: 'box')
                violin_width_scale: The method used to scale the width of the violin plot. Either "area", "count" or "width" (default: "width")
                box_iqr: The proportion past the lower and upper quartiles to extend the plot whiskers for the box plot. Points outside this range will be identified as outliers (default: 1.5)
                saveImage: Setting to 'True' will save the image to file (default: True)
                imageFileName: The image file name to save to (default: [plot_type]_features.png')                
                dpi: The number of Dots Per Inch (DPI) for the image (default: 200)

            help : Print this help text

            plot : Generates feature plots
    """

    def __init__(self, peaktable, datatable):

        peaktable = self.__checkPeakTable(self.__checkData(peaktable))
        datatable = self.__checkData(datatable)

        # Slice the meta-data, and select only peaks from the peaktable for processing, and add the meta-data back
        meta = datatable.T[~datatable.T.index.isin(peaktable['Name'])].T.reset_index(drop=True)
        dat = datatable[peaktable['Name']].reset_index()
        datatable = pd.concat([meta, dat], axis=1).set_index(['index'])
        datatable.index.name = None

        self.__peaktable = peaktable

        # Search for duplicate labels and amend with a suffix, to avoid issues when relabelling the datatable
        labels = copy.deepcopy(list(peaktable['Label']))
        label_counts = {k: v for k, v in Counter(labels).items() if v > 1}

        for i in reversed(range(len(labels))):
            item = str(labels[i])
            if item in label_counts and label_counts[item]:
                labels[i] += "_" + str(label_counts[item])
                label_counts[item] -= 1

        #Label datatable with peak labels instead of names for ease of feature plotting
        col_label_dict = dict(zip(list(peaktable['Name']), labels))
        datatable.rename(columns=col_label_dict, inplace=True)

        self.__peak_labels = labels

        self.__datatable = datatable

        self.set_params()

    def help(self):
        print(plotFeatures.usage)

    def set_params(self, plot_type='point', column_numbers=4, log_data=(True, 2), scale_data=(True, 'minmax'), impute_data=(True, 3), style='seaborn-white', transparent=False, figSize = (15, 10), fontSize = 12, colour_palette=None, y_axis_label=None, x_axis_rotation=0, group_column_name=None, point_estimator='mean', point_ci=95, violin_distribution_type='box', violin_width_scale='width', box_iqr=1.5, saveImage=True, imageFileName='_features.png', dpi = 200):

        plot_type, column_numbers, log_data, scale_data, impute_data, style, transparent, figSize, fontSize, colour_palette, y_axis_label, x_axis_rotation, group_column_name, point_estimator, point_ci, violin_distribution_type, violin_width_scale, box_iqr, saveImage, imageFileName, dpi = self.__paramCheck(plot_type, column_numbers, log_data, scale_data, impute_data, style, transparent, figSize, fontSize, colour_palette, y_axis_label, x_axis_rotation, group_column_name, point_estimator, point_ci, violin_distribution_type, violin_width_scale, box_iqr, saveImage, imageFileName, dpi)

        self.__plot_type = plot_type;
        self.__column_numbers = column_numbers;
        self.__log_data = log_data;
        self.__scale_data = scale_data;
        self.__impute_data = impute_data;
        self.__style = style;
        self.__transparent = transparent;
        self.__figSize = figSize;
        self.__fontSize = fontSize;
        self.__colour_palette = colour_palette;
        self.__y_axis_label = y_axis_label;
        self.__x_axis_rotation = x_axis_rotation;
        self.__group_column_name = group_column_name;
        self.__point_estimator = point_estimator;
        self.__point_ci = point_ci;
        self.__violin_distribution_type = violin_distribution_type;
        self.__violin_width_scale = violin_width_scale;
        self.__box_iqr = box_iqr;
        self.__saveImage = saveImage;
        self.__imageFileName = imageFileName;
        self.__dpi = dpi;

    def plot(self):

        datatable = copy.deepcopy(self.__datatable)
        labels = self.__peak_labels
        plot_type = self.__plot_type
        group_column_name = self.__group_column_name
        column_numbers = self.__column_numbers
        colour_palette = self.__colour_palette
        point_ci = self.__point_ci
        point_estimator = self.__point_estimator
        log_data = self.__log_data
        scale_data = self.__scale_data
        impute_data = self.__impute_data
        x_axis_rotation = self.__x_axis_rotation
        y_axis_label = self.__y_axis_label
        violin_distribution_type = self.__violin_distribution_type
        violin_width_scale = self.__violin_width_scale
        box_iqr = self.__box_iqr
        imageFileName = self.__imageFileName
        saveImage = self.__saveImage
        fontSize = self.__fontSize
        style = self.__style
        transparent = self.__transparent
        dpi = self.__dpi
        figSize = self.__figSize

        meta = datatable.T[~datatable.T.index.isin(labels)].T.reset_index(drop=True)
        X = datatable[labels].reset_index(drop=True)

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
            X = pd.DataFrame(X, columns=labels)

        # Add the meta data back in with the logged, scaled, or imputed data
        datatable = pd.concat([meta, X], axis=1).reset_index(drop=True)

        with plt.style.context(style):
            fig, axes = plt.subplots(nrows=int(np.ceil(float(len(labels) / column_numbers))), ncols=column_numbers, sharey=True, figsize=figSize)

            if plot_type == 'point':

                for peak_index, peak in enumerate(labels):
                    if point_estimator.lower() == 'mean':
                        point_estimator = 'Mean'
                        ax = sns.pointplot(data=datatable, x=group_column_name, y=peak, estimator=np.nanmean, capsize=0.1, ci=point_ci, palette=colour_palette, ax=axes.flat[peak_index])
                    elif point_estimator.lower() == 'median':
                        point_estimator = 'Median'
                        ax = sns.pointplot(data=datatable, x=group_column_name, y=peak, estimator=np.nanmedian, capsize=0.1, ci=point_ci, palette=colour_palette, ax=axes.flat[peak_index])
                    else:
                        print("Error: Invalid point plot estimator type.")
                        sys.exit()

                    ax.tick_params(labelrotation=x_axis_rotation, labelsize=fontSize)

                    if log_bool:
                        if scale_data:
                            if isinstance(point_ci, str):
                                if point_ci == 'sd':
                                    ax.set_title(peak + ' within SD', fontsize=fontSize)
                                    ax.set_xlabel('')
                                    if y_axis_label is None:
                                        ax.set_ylabel('Log({}) scaled ({}) {} Peak Area within SD'.format(log_base, scale_type, point_estimator), fontsize=fontSize)
                                    else:
                                        ax.set_ylabel(y_axis_label, fontsize=fontSize)
                            else:
                                ax.set_title(peak + ' with {}% CI'.format(point_ci), fontsize=fontSize)
                                ax.set_xlabel('')
                                if y_axis_label is None:
                                    ax.set_ylabel('Log({}) scaled ({}) {} Peak Area & {}% CI'.format(log_base, scale_type, point_estimator, point_ci), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                        else:
                            if isinstance(point_ci, str):
                                if point_ci == 'sd':
                                    ax.set_title(peak + ' within SD', fontsize=fontSize)
                                    ax.set_xlabel('')
                                    if y_axis_label is None:
                                        ax.set_ylabel('Log({}) {} Peak Area within SD'.format(log_base, point_estimator), fontsize=fontSize)
                                    else:
                                        ax.set_ylabel(y_axis_label, fontsize=fontSize)
                            else:
                                ax.set_title(peak + ' with {}% CI'.format(point_ci), fontsize=fontSize)
                                ax.set_xlabel('')
                                if y_axis_label is None:
                                    ax.set_ylabel('Log({}) {} Peak Area & {}% CI'.format(log_base, point_estimator, point_ci), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                    else:
                        if scale_data:
                            if isinstance(point_ci, str):
                                if point_ci == 'sd':
                                    ax.set_title(peak + ' within SD', fontsize=fontSize)
                                    ax.set_xlabel('')
                                    if y_axis_label is None:
                                        ax.set_ylabel('Scaled ({}) {} Peak Area within SD'.format(scale_type, point_estimator), fontsize=fontSize)
                                    else:
                                        ax.set_ylabel(y_axis_label, fontsize=fontSize)
                            else:
                                ax.set_title(peak + ' with {}% CI'.format(point_ci), fontsize=fontSize)
                                ax.set_xlabel('')
                                if y_axis_label is None:
                                    ax.set_ylabel('Scaled ({}) {} Peak Area & {}% CI'.format(scale_type, point_estimator, point_ci), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)
                        else:
                            if isinstance(point_ci, str):
                                if point_ci == 'sd':
                                    ax.set_title(peak + ' within SD', fontsize=fontSize)
                                    ax.set_xlabel('')
                                    if y_axis_label is None:
                                        ax.set_ylabel('{} Peak Area within SD'.format(point_estimator), fontsize=fontSize)
                                    else:
                                        ax.set_ylabel(y_axis_label, fontsize=fontSize)
                            else:
                                ax.set_title(peak + ' with {}% CI'.format(point_ci), fontsize=fontSize)
                                ax.set_xlabel('')
                                if y_axis_label is None:
                                    ax.set_ylabel('{} Peak Area & {}% CI'.format(point_estimator, point_ci), fontsize=fontSize)
                                else:
                                    ax.set_ylabel(y_axis_label, fontsize=fontSize)

            elif plot_type.lower() == 'violin':
                for peak_index, peak in enumerate(labels):

                    ax = sns.violinplot(data=datatable, x=group_column_name, y=peak, linewidth=1, inner=violin_distribution_type, scale=violin_width_scale, palette=colour_palette, ax=axes.flat[peak_index])

                    ax.tick_params(labelrotation=x_axis_rotation, labelsize=fontSize)

                    ax.set_title(peak, fontsize=fontSize)
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
                for peak_index, peak in enumerate(labels):

                    ax = sns.boxplot(data=datatable, x=group_column_name, y=peak, palette=colour_palette, whis=box_iqr, ax=axes.flat[peak_index])

                    ax.tick_params(labelrotation=x_axis_rotation, labelsize=fontSize)

                    ax.set_title(peak, fontsize=fontSize)
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
                for peak_index, peak in enumerate(labels):

                    ax = sns.swarmplot(data=datatable, x=group_column_name, y=peak, size=10, palette=colour_palette, ax=axes.flat[peak_index])

                    ax.tick_params(labelrotation=x_axis_rotation, labelsize=fontSize)

                    ax.set_title(peak, fontsize=fontSize)
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
                for peak_index, peak in enumerate(labels):
                    ax = sns.violinplot(data=datatable, x=group_column_name, y=peak, linewidth=1, inner=None, scale=violin_width_scale, palette=colour_palette, ax=axes.flat[peak_index])
                    ax = sns.swarmplot(data=datatable, x=group_column_name, y=peak, color="white", edgecolor="gray", ax=axes.flat[peak_index])

                    ax.tick_params(labelrotation=x_axis_rotation, labelsize=fontSize)

                    ax.set_title(peak, fontsize=fontSize)
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
                for peak_index, peak in enumerate(labels):
                    ax = sns.boxplot(data=datatable, x=group_column_name, y=peak, palette=colour_palette, whis=np.inf, ax=axes.flat[peak_index])
                    ax = sns.swarmplot(data=datatable, x=group_column_name, y=peak, color="0.2", ax=axes.flat[peak_index])

                    ax.tick_params(labelrotation=x_axis_rotation, labelsize=fontSize)

                    ax.set_title(peak, fontsize=fontSize)
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

    def __paramCheck(self, plot_type, column_numbers, log_data, scale_data, impute_data, style, transparent, figSize, fontSize, colour_palette, y_axis_label, x_axis_rotation, group_column_name, point_estimator, point_ci, violin_distribution_type, violin_width_scale, box_iqr, saveImage, imageFileName, dpi):

        cmap_list = list(matplotlib.cm.cmaps_listed) + list(matplotlib.cm.datad)
        cmap_list_r = [cmap + '_r' for cmap in cmap_list]
        cmap_list = cmap_list + cmap_list_r

        plot_types = ['point', 'violin', 'box', 'swarm', 'violin-swarm', 'box-swarm']
        estimator_types = ['mean', 'median']

        datatable = self.__datatable

        if plot_type.lower() not in plot_types:
            print("Error: Plot type is not valid. Choose one of the following: {}.".format(', '.join(plot_types)))
            sys.exit()

        if not isinstance(column_numbers, int):
            print("Error: Column numbers is not valid. Choose a integer value.")
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
                print("Error: Scale data second tuple item is not valid. Choose one of {}.".format(', '.join(scale_types)))
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

        if colour_palette is not None:
            if not isinstance(colour_palette, str):
                print("Error: The colour palette is not valid. Choose a string value.")
                sys.exit()
            else:
                if colour_palette not in cmap_list:
                    print("Error: The colour palette is not valid. Choose one of the following: {}.".format(', '.join(cmap_list)))
                    sys.exit()

        if y_axis_label is not None:
            if isinstance(y_axis_label, str):
                print("Error: The y axis label is not valid. Choose a string value.")
                sys.exit()

        if not isinstance(x_axis_rotation, float):
            if not isinstance(x_axis_rotation, int):
                print("Error: The x axis rotation value is not valid. Choose a float or integer value.")
                sys.exit()

        if ((x_axis_rotation < 0) or (x_axis_rotation > 360)):
            print("Error: The x axis rotation value is not valid. Choose a value >=0 or <= 360.")
            sys.exit()

        if group_column_name is not None:
            if not isinstance(group_column_name, str):
                print("Error: Group column name is not valid. Choose a string value.")
                sys.exit()
            else:
                if group_column_name not in list(datatable.columns):
                    print("Error: Group column name not valid. Choose one of {}.".format(', '.join(list(datatable.columns))))
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
                    print(
                        "Error: The box plot interquartile range extension beyond whiskers is not valid. Choose a float or integer value.")
                    sys.exit()

        if not isinstance(saveImage, bool):
            print("Error: Save image is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(imageFileName, str):
            print("Error: Image file name is not valid. Choose a string value.")
            sys.exit()

        if not isinstance(dpi, float):
            if not isinstance(dpi, int):
                print("Error: Dpi is not valid. Choose a float or integer value.")
                sys.exit()

        return plot_type, column_numbers, log_data, scale_data, impute_data, style, transparent, figSize, fontSize, colour_palette, y_axis_label, x_axis_rotation, group_column_name, point_estimator, point_ci, violin_distribution_type, violin_width_scale, box_iqr, saveImage, imageFileName, dpi

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

        # Do not assume the peaks/nodes have been indexed correctly. Remove any index columns and reindex.
        column_list = [column.lower() for column in PeakTable.columns]
        if 'idx' in column_list:
            index = column_list.index('idx')
            column_name = PeakTable.columns[index]
            PeakTable = PeakTable.drop(columns=[column_name])

        if 'index' in column_list:
            index = column_list.index('index')
            column_name = PeakTable.columns[index]
            PeakTable = PeakTable.drop(columns=[column_name])

        PeakTable = PeakTable.reset_index(drop=True)

        PeakTable.index.name = 'Idx'

        PeakTable = PeakTable.reset_index()

        return PeakTable