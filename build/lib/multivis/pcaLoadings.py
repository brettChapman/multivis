import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import scikits.bootstrap as bootstrap
from sklearn.decomposition import PCA
from collections import Counter
import warnings

def pcaLoadings(data, peak_label, imageFileName='PCA_loadings.png', saveImage=True, dpi=200, pc_num=1, bootnum=10000, alpha=0.05, fontSize=30, markerSize=100, figSize=(40,40), transparent=False):
    """Creates a PCA Loadings lollipop plot.

        Parameters
        -------------------
        data: array-like, shape (n_samples, n_features)
        peak_label: A list of peaks to plot
        imageFileName: The image file name to save to (default: 'PCA_loadings.png')
        saveImage: Setting to 'True' will save the image to file (default: True)
        dpi: The number of Dots Per Inch (DPI) for the image (default: 200)
        pc_num: The principal component to plot (default: 1)
        boot_num: The number of bootstrap samples to use to calculate confidence internals (default: 10000)
        alpha: The alpha value for the bootstrapped confidence intervals (default: 0.05)
        fontSize: The font size for all text (default: 30)
        markerSize: The size of each marker (default: 100)
        figSize: The figure size as a tuple (width,height) (default: (40,40))
        transparent: Setting to 'True' will make the background transparent (default: False)
    """

    font = {'family': 'Times New Roman', 'size': fontSize}

    matplotlib.rc('font', **font)

    pca = PCA(n_components=2)
    pca.fit_transform(data)

    df_loadings = pd.DataFrame(pca.components_.T, columns=['1', '2'])

    bootpca = lambda x: __boot_pca(x, pca.components_.T, pc_num)

    # Filter out instability warnings only for bootstrapped PCA CI (other statfunctions e.g. np.median across groups don't give warnings)
    warnings.simplefilter("ignore")

    PCA_CIs = bootstrap.ci(data=data, statfunction=bootpca, n_samples=bootnum, alpha=alpha)

    # Reinstate warnings for other functions
    warnings.simplefilter("default")

    fig, ax = plt.subplots(figsize=figSize)

    pc_loadings = []
    pc_lower = []
    pc_upper = []
    
    #Search for duplicate labels and amend with a suffix
    counts = {k:v for k,v in Counter(list(peak_label)).items() if v > 1}
    peakNames = list(peak_label)[:]

    for i in reversed(range(len(list(peak_label)))):
        item = str(list(peak_label)[i])
        if item in counts and counts[item]:
            peakNames[i] += "_" + str(counts[item])
            counts[item]-=1

    peakList = zip(peakNames, df_loadings[str(pc_num)].values, PCA_CIs[0,:], PCA_CIs[1,:])

    peakNames, pc_load, pc_ll, pc_ul = list(zip(*peakList))

    for idx, peakName in enumerate(peakNames):
            pc_loadings = np.append(pc_loadings, [pc_load[idx]])

            pc_lower = np.append(pc_lower, [pc_ll[idx]])
            pc_upper = np.append(pc_upper, [pc_ul[idx]])

    pc_ul = np.subtract(pc_upper, pc_loadings)
    pc_ll = np.subtract(pc_loadings, pc_lower)

    pc_error = np.vstack((pc_ll, pc_ul))

    sigPlots = np.add(np.sign(np.multiply(pc_lower, pc_upper)), 1).astype(bool);

    colors = []
    for TF in sigPlots:
        if TF:
            colors.append('red')
        else:
            colors.append('black')

    ax.scatter(peakNames, pc_loadings, c=colors, marker='o', s=markerSize)
    ax.errorbar(peakNames, pc_loadings, yerr=pc_error, ecolor=colors, fmt='none', zorder=-1)

    ax.axhline(y=0, color='k')
    ax.set_xlim(-1, len(peakNames)+1)
    ax.set_title("PC{} Loadings with {}% CI".format(str(pc_num), 100*(1-alpha)), fontsize=fontSize)
    ax.set_ylabel("PC{} Loadings & {}% CI".format(str(pc_num), 100*(1-alpha)), fontsize=fontSize)
    ax.set_xlabel("")

    ax.tick_params(labelsize=fontSize, rotation=90)

    ax.patch.set_alpha(1.0)

    plt.show()
    
    if saveImage:
        fig.savefig(imageFileName, dpi=dpi, transparent=transparent)

def __boot_pca(X, score, n):
    pca = PCA(n_components=2)
    pca.fit_transform(X)
    coeff = pca.components_.T

    rho = np.corrcoef(score[:, n - 1], coeff[:, n - 1], rowvar=False)[0][1]

    if np.sign(rho) == -1:
        C = np.multiply(coeff[:, n - 1], -1)
    else:
        C = np.multiply(coeff[:, n - 1], 1)

    return C