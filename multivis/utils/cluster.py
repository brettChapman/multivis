import numpy as np
import pandas as pd
import scipy.spatial as sp, scipy.cluster.hierarchy as hc
from scipy.spatial.distance import squareform

def cluster(X, transpose_non_correlated, is_correlated, distance_metric, linkage_method):
    """Performs linkage clustering given a matrix of correlations. If no correlated data is presented, then calculates spatial distance
    given a distance metric such as Euclidean distance, then applies the linkage clustering method.
        Parameters
        ----------
        X : A Pandas dataframe matrix of values (may or may not be a matrix of correlation coefficients)

        transpose_non_correlated : Setting to 'True' will transpose the matrix if it is not correlated data

        is_correlated : Setting to 'True' will treat the matrix as if it contains correlation coefficients

        distance_metric : Set the distance metric. Used if the matrix does not contain correlation coefficients.

        linkage_method : Set the linkage method for the clustering.

        Returns
        -------
        X : The original matrix, transposed if transpose_non_correlated is 'True' and is_correlated is 'False'.
        row_linkage : linkage matrix for the rows from a linkage clustered scores matrix
        col_linkage : linkage matrix for the columns from a linkage clustered scores matrix
    """

    X, transpose_non_correlated, is_correlated, distance_metric, linkage_method = __checkData(X, transpose_non_correlated, is_correlated, distance_metric, linkage_method)

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

def __checkData(X, transpose_non_correlated, is_correlated, distance_metric, linkage_method):

    VALID_METRICS = ['euclidean', 'l2', 'l1', 'manhattan', 'cityblock', 'braycurtis', 'canberra', 'chebyshev', 'correlation',
                     'cosine', 'dice', 'hamming', 'jaccard', 'kulsinski', 'mahalanobis', 'matching', 'minkowski', 'rogerstanimoto',
                     'russellrao', 'seuclidean', 'sokalmichener', 'sokalsneath', 'sqeuclidean', 'yule', 'wminkowski', 'haversine']

    LINKAGE_METHODS = ['single', 'complete', 'average', 'centroid', 'median', 'ward', 'weighted']

    EUCLIDEAN_LINKAGE_METHODS = ['centroid', 'median', 'ward']

    if not isinstance(X, pd.DataFrame):
        print("Error: A dataframe was not entered. Please check your data.")
        sys.exit()

    if not type(transpose_non_correlated) == bool:
        print("Error: transpose_non_correlated is not valid. Choose either \"True\" or \"False\".")
        sys.exit()

    if not type(is_correlated) == bool:
        print("Error: is_correlated is not valid. Choose either \"True\" or \"False\".")
        sys.exit()

    if distance_metric.lower() not in VALID_METRICS:
        print("Error: Distance metric not valid. Choose one of the following: {}.".format(', '.join(VALID_METRICS)))
        sys.exit()

    if linkage_method.lower() not in LINKAGE_METHODS:
        print("Error: Linkage method not valid. Choose one of the following: {}.".format(', '.join(LINKAGE_METHODS)))
        sys.exit()

    if linkage_method.lower() in EUCLIDEAN_LINKAGE_METHODS and distance_metric.lower() != 'euclidean':
        print("Error: Method {} requires the distance metric to be Euclidean.".format(linkage_method.lower()))
        sys.exit()

    return X, transpose_non_correlated, is_correlated, distance_metric, linkage_method