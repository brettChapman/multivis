import copy
import matplotlib
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, dendrogram
import numpy as np
import pandas as pd

def smoothsegment(seg, Nsmooth=100):
    return np.concatenate([[seg[0]], np.linspace(seg[1], seg[2], Nsmooth), [seg[3]]])

def cartesian_to_polar(x, y):
    rho = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x)
    return (rho, phi)

def generateDendrogram(matrix, peakLabels, distance_metric, linkage_method, color_threshold):

    Y = pdist(matrix, distance_metric)
    Z = linkage(Y, linkage_method)

    dn = dendrogram(Z, labels=peakLabels, no_plot=True, color_threshold=color_threshold)

    return dn

def polarDendrogram(imageFileName, saveImage, dendrogram, branch_offset, gap, grid, text_colors_dict, label_dict, fontSize, style_sheet, figsize):

    icoord = np.array(dendrogram['icoord'], dtype=float)
    dcoord = np.array(dendrogram['dcoord'], dtype=float)
    idx_labels = np.array(dendrogram['ivl'])
    colors = np.array(dendrogram['color_list'])

    dcoord = -np.log(dcoord + branch_offset)

    imax = icoord.max()
    imin = icoord.min()

    icoord = ((icoord - imin) / (imax - imin) * (1 - gap) + gap / 2) * 2 * np.pi

    with plt.style.context(style_sheet):
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, polar=True)

        #ax.set_rmax(2)
        #ax.set_rlabel_position(0)

        angleRange = []
        for xs, ys, c in zip(icoord, dcoord, colors):

            xs = smoothsegment(xs)
            ys = smoothsegment(ys)

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

            lab = ax.text(x, y, label_dict[int(label.get_text())], color=text_colors_dict[int(label.get_text())], fontsize=fontSize, rotation=theta, transform=label.get_transform(), rotation_mode="anchor", ha=ha, va="center")#, bbox=dict(facecolor = "none", edgecolor ="red"))

            xlabels.append(lab)
        ax.set_xticklabels([])

        ax.grid(grid)

        if saveImage:
            plt.savefig(imageFileName, format="JPG");

        plt.show()