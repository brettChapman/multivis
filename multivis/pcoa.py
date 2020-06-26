import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import MDS
import seaborn as sns

def pcoa(similarities, imageFileName='PCOA.png', saveImage=True, dpi=200, n_components=2, max_iter=300, eps=1e-3, seed=3, group_label=None, peak_label=None, markerSize=100, fontSize=12, figSize=(20,10), cmap='Set1'):
    """Creates a PCoA scores plot.

    Parameters
    -------------------
    similarities: array-like matrix, shape (n_samples, n_features)
    imageFileName: The image file name to save to (default: 'PCOA.png')
    saveImage: Setting to 'True' will save the image to file (default: True)
    dpi: The number of Dots Per Inch (DPI) for the image (default: 200)
    n_components: Number of components (default: 2)
    max_iter: Maximum number of iterations of the SMACOF algorithm (default: 300)
    eps: Relative tolerance with respect to stress at which to declare convergence (default: 1e-3)
    seed: Seed number used by the random number generator for the RandomState instance (default: 3)
    group_label: Labels to assign to each group/class (default: None)
    peak_label: Labels to assign to each peak (default: None)
    markerSize: The size of each marker (default: 100)
    fontSize: The font size set for each node (default: 12)
    figSize: The figure size as a tuple (width,height) (default: (20,10))
    cmap: The CMAP colour palette to use (default: 'Set1')
    """

    markers = ['o', 'v', '^', '<', '>', 'H', 'D', 'X', 'P', 'd', '8', 's', 'p', '*', 'h']

    seed = np.random.RandomState(seed=seed)

    mds = MDS(n_components=n_components, max_iter=max_iter, eps=eps, random_state=seed, dissimilarity="precomputed", n_jobs=1)

    Y = mds.fit(similarities).embedding_

    pca = PCA()
    Y = pca.fit_transform(Y)
    x_score = Y[:, 0]
    y_score = Y[:, 1]

    explained_variance = pca.explained_variance_ratio_ * 100
    x_expvariance = explained_variance[n_components-2]
    y_expvariance = explained_variance[n_components-1]

    fig, ax = plt.subplots(figsize=figSize)

    if list(peak_label) != None:
        for i, txt in enumerate(list(peak_label)):
            ax.annotate(txt, (x_score[i]+.001, y_score[i]), fontsize=fontSize)

    sns.scatterplot(x=x_score, y=y_score, hue=group_label, s=markerSize, markers=markers, style=group_label, palette=cmap)

    ax.set_title('PCoA Plot')

    ax.set_xlabel("PCo1 ({:0.1f}%)".format(x_expvariance))
    ax.set_ylabel("PCo2 ({:0.1f}%)".format(y_expvariance))

    ax.grid()

    if saveImage:
        fig.savefig(imageFileName, dpi=dpi)