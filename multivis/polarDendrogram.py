import sys
import copy
import matplotlib
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram
import numpy as np
import pandas as pd

class polarDendrogram:
    """Class for polarDendrogram to produce a polar dendrogram given a cartesian dendrogram

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
                style_sheet: Setting the Seaborn style-sheet (see https://python-graph-gallery.com/104-seaborn-themes/) (default: 'seaborn-white')
                dpi: The number of Dots Per Inch (DPI) for the image (default: 200)
                figSize: The figure size as a tuple (width,height) (default: (10,10))
                fontSize: The font size for all text (default: 15)
                PeakTable: The Peak Table Pandas dataframe (default: empty dataframe)
                Color_column: The colour column to use from Peak Table (Can be colour or numerical values such as 'pvalue') (default: 'black')
                Label_column: The label column to use from Peak Table (default: use original Peak Table index from cartesian dendrogram)
                text_cmap: The CMAP colour palette to use (default: 'brg')

            run : Generates and displays the Polar dendrogram.
    """

    def __init__(self, dn):

        self.__dn = self.__checkData(dn)

        self.set_params()

    def set_params(self, imageFileName='polarDendrogram.png', saveImage=True, branch_scale='linear', gap=0.1, grid=False, style_sheet='seaborn-white', dpi=200, figSize=(10,10), fontSize=15, PeakTable=pd.DataFrame(), Color_column=None, Label_column=None, text_cmap='brg'):

        text_colors, labels = self.__checkPeakTable(PeakTable, Color_column, Label_column, text_cmap)

        imageFileName, saveImage, branch_scale, gap, grid, style_sheet, dpi, figSize, fontSize = self.__paramCheck(imageFileName, saveImage, branch_scale, gap, grid, style_sheet, dpi, figSize, fontSize)

        self.__imageFileName = imageFileName;
        self.__saveImage = saveImage;
        self.__branch_scale = branch_scale;
        self.__gap = gap;
        self.__grid = grid;
        self.__style_sheet = style_sheet;
        self.__dpi = dpi;
        self.__figSize = figSize;
        self.__fontSize = fontSize;
        self.__text_colors = text_colors;
        self.__labels = labels;

    def run(self):

        imageFileName = self.__imageFileName
        saveImage = self.__saveImage
        dendrogram = self.__dn
        branch_scale = self.__branch_scale
        gap = self.__gap
        grid = self.__grid
        text_colors = self.__text_colors
        labels = self.__labels
        fontSize = self.__fontSize
        style_sheet = self.__style_sheet
        dpi = self.__dpi
        figSize = self.__figSize

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

        with plt.style.context(style_sheet):
            fig = plt.figure(figsize=figSize)
            ax = fig.add_subplot(111, polar=True)

            #ax.set_rmax(2)
            #ax.set_rlabel_position(0)

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
                    lab = ax.text(x, y+0.05, labels[int(label.get_text())], color=text_colors[int(label.get_text())], fontsize=fontSize, rotation=theta, transform=label.get_transform(), rotation_mode="anchor", ha=ha, va="center")
                elif not labels and not text_colors:
                    lab = ax.text(x, y+0.05, label.get_text(), color="black", fontsize=fontSize, rotation=theta, transform=label.get_transform(), rotation_mode="anchor", ha=ha, va="center")
                elif labels:
                    lab = ax.text(x, y+0.05, labels[int(label.get_text())], color="black", fontsize=fontSize, rotation=theta, transform=label.get_transform(), rotation_mode="anchor", ha=ha, va="center")
                elif text_colors:
                    lab = ax.text(x, y+0.05, label.get_text(), color=text_colors[int(label.get_text())], fontsize=fontSize, rotation=theta, transform=label.get_transform(), rotation_mode="anchor", ha=ha, va="center")

                xlabels.append(lab)

            ax.set_xticklabels([])

            ax.grid(grid)

            if saveImage:
                plt.savefig(imageFileName, dpi=dpi);

            plt.show()

    def __checkData(self, dn):

        if not isinstance(dn, dict):
            print("Error: A dendrogram dictionary was not entered. Please check your data.")
            sys.exit()

        return dn

    def __checkPeakTable(self, PeakTable, Color_column, Label_column, text_cmap):

        if not isinstance(text_cmap, str):
            print("Error: Text CMAP is not valid. Choose a string value.")
            sys.exit()
        else:
            cmap_list = matplotlib.cm.cmap_d.keys()

            if text_cmap not in cmap_list:
                print("Error: Text CMAP is not valid. Choose one of the following: {}.".format(', '.join(cmap_list)))
                sys.exit()

        if not isinstance(PeakTable, pd.DataFrame):
            print("Error: Provided Peak Table is not valid. Choose a Pandas dataframe.")
            sys.exit()
        else:
            if PeakTable.empty:
                text_colors = {}
                labels = {}
            else:
                textCmap = plt.cm.get_cmap(text_cmap)  # Sets the color palette for the text

                PeakTable_columns = list(PeakTable.columns);

                if Color_column in PeakTable_columns:
                    colorsHEX = []

                    for colorValue in PeakTable[Color_column].values:
                        if matplotlib.colors.is_color_like(colorValue):
                            text_colors = dict(zip(PeakTable.index, PeakTable[Color_column]))
                            break;
                        elif isinstance(colorValue, float):
                            colorsRGB = self.__get_colors(PeakTable[Color_column].values, textCmap)[:, :3]

                            for rgb in colorsRGB:
                                colorsHEX.append(matplotlib.colors.rgb2hex(rgb))

                            text_colors = dict(zip(PeakTable.index, colorsHEX))

                            break;
                        elif isinstance(colorValue, int):
                            colorsRGB = self.__get_colors(PeakTable[Color_column].values, textCmap)[:, :3]

                            for rgb in colorsRGB:
                                colorsHEX.append(matplotlib.colors.rgb2hex(rgb))

                            text_colors = dict(zip(PeakTable.index, colorsHEX))

                            break;
                        else:
                            print("Error: Colour column is not valid. Choose colour values, floats or integer values.")
                            sys.exit()
                elif Color_column == None:
                    text_colors = {}
                else:
                    print("Error: Provided Color_column is not in Peak Table. Choose a valid colour column.")
                    sys.exit()

                if Label_column in PeakTable_columns:
                    labels = dict(zip(PeakTable.index, PeakTable[Label_column]))
                elif Label_column == None:
                    labels = {}
                else:
                    print("Error: Provided Label_column is not in Peak Table. Choose a valid label column.")
                    sys.exit()

        return text_colors, labels

    def __paramCheck(self, imageFileName, saveImage, branch_scale, gap, grid, style_sheet, dpi, figSize, fontSize):

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

        if not isinstance(style_sheet, str):
            print("Error: Style sheet is not valid. Choose a string value.")
            sys.exit()
        else:
            styleList = list(plt.style.available)

            if style_sheet not in styleList:
                print("Error: Chosen style sheet is not valid. Choose one of the following: {}.".format(', '.join(styleList)))
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

        return imageFileName, saveImage, branch_scale, gap, grid, style_sheet, dpi, figSize, fontSize

    def __smoothsegment(self, seg, Nsmooth=100):
        return np.concatenate([[seg[0]], np.linspace(seg[1], seg[2], Nsmooth), [seg[3]]])

    def __get_colors(self, x, cmap):
        norm = matplotlib.colors.Normalize(vmin=x.min(), vmax=x.max())

        return cmap(norm(x))