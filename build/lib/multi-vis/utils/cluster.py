import numpy as np
import pandas as pd
import scipy.spatial as sp, scipy.cluster.hierarchy as hc
from scipy.spatial.distance import squareform

def cluster(X, transpose_non_correlated, is_correlated, distance_metric, linkage_method):

    if is_correlated:

        Z = (X.values + X.values.T) / 2

        np.fill_diagonal(Z, 1)

        dissimilarity = 1 - np.abs(Z)

        linkage = hc.linkage(squareform(dissimilarity), linkage_method)

        row_linkage = linkage;
        col_linkage = linkage;
    else:
        if transpose_non_correlated:
            X = X.T

        row_linkage, col_linkage = (hc.linkage(sp.distance.pdist(x, distance_metric), linkage_method)
                                    for x in (X.values, X.values.T))

    return X, row_linkage, col_linkage