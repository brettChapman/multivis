import pandas as pd
import scipy.spatial as sp, scipy.cluster.hierarchy as hc

def spatialClustering(X, transpose, distance_metric, linkage_method):

    if transpose:
        X = X.T

    row, col = X.shape;

    if row > col:
        X = X.T

    Y = sp.distance.pdist(X, distance_metric)
    Z = hc.linkage(Y, linkage_method)

    row_linkage, col_linkage = (hc.linkage(sp.distance.pdist(x, distance_metric), linkage_method)
                                for x in (X.values, X.values.T))

    if row > col:
        row_temp = row_linkage;
        col_temp = col_linkage;

        col_linkage = row_temp;
        row_linkage = col_temp;

    X.index.name = ''
    X.columns.name = ''

    return X, Z, row_linkage, col_linkage