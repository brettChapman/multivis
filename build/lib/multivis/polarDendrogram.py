import sys
import copy
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram
import numpy as np
import pandas as pd

class polarDendrogram:
    """Class for plotNetwork to produce a static spring-embedded network.

            Parameters
            ----------
            dn : Dendrogram dictionary.

            Methods
            -------
            set_params : Set parameters - image file name, save image flag, dendrogram branch scale type ('linear', 'log', 'square'), gap value, display grid flag, style-sheet type, dpi, figure size
                                            , text parameters dictionary(font size, text colours dictionary(index from peak table: values as colours), text labels dictionary(index from peak table: values as labels from peak table))
            run : Generates and displays the Polar dendrogram.
    """

    def __init__(self, dn):

        self.__dn = self.__checkData(dn)

        self.set_params()
        self.__set_text_params()

    def set_params(self, imageFileName='polarDendrogram.png', saveImage=True, branch_scale='linear', gap=0.1, grid=False, style_sheet='seaborn-white', dpi=200, figSize=(10,10), text_params={}):

        if text_params:
            self.__set_text_params(**text_params)

        imageFileName, saveImage, branch_scale, gap, grid, style_sheet, dpi, figSize = self.__paramCheck(imageFileName, saveImage, branch_scale, gap, grid, style_sheet, dpi, figSize)

        self.__imageFileName = imageFileName;
        self.__saveImage = saveImage;
        self.__branch_scale = branch_scale;
        self.__gap = gap;
        self.__grid = grid;
        self.__style_sheet = style_sheet;
        self.__dpi = dpi;
        self.__figSize = figSize;

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

    def __set_text_params(self, fontSize=15, text_colors={}, labels={}):

        fontSize, text_colors, labels = self.__text_paramCheck(fontSize, text_colors, labels)

        self.__fontSize = fontSize;
        self.__text_colors = text_colors;
        self.__labels = labels;

    def __paramCheck(self, imageFileName, saveImage, branch_scale, gap, grid, style_sheet, dpi, figSize):

        if not isinstance(imageFileName, str):
            print("Error: Image file name is not valid. Choose a string value.")
            sys.exit()

        if not type(saveImage) == bool:
            print("Error: Save image is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if branch_scale.lower() not in ["linear", "log", "square"]:
            print("Error: Branch scale not valid. Choose either \"linear\", \"log\" or \"square\".")

        if not isinstance(gap, float):
            if not isinstance(gap, int):
                print("Error: Gap is not valid. Choose a float or integer value.")
                sys.exit()

        if not type(grid) == bool:
            print("Error: Grid is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(style_sheet, str):
            print("Error: Style sheet is not valid. Choose a string value.")
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

        return imageFileName, saveImage, branch_scale, gap, grid, style_sheet, dpi, figSize

    def __text_paramCheck(self, fontSize, text_colors, labels):

        if not isinstance(fontSize, float):
            if not isinstance(fontSize, int):
                print("Error: Font size is not valid. Choose a float or integer value.")
                sys.exit()

        if not text_colors:
            if not isinstance(text_colors, dict):
                print("Error: Text colours is not valid. Use a dictionary with Peak Table indexes as keys and associated colours as values.")
                sys.exit()

        if not labels:
            if not isinstance(labels, dict):
                print("Error: Labels is not valid. Use a dictionary with Peak Table indexes as keys and associated labels as values.")
                sys.exit()

        return fontSize, text_colors, labels

    def __smoothsegment(self, seg, Nsmooth=100):
        return np.concatenate([[seg[0]], np.linspace(seg[1], seg[2], Nsmooth), [seg[3]]])