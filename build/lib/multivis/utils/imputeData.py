import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer

def imputeData(data, k=3):

    try:
        data_array = data.select_dtypes(include=float).values
        imputer = KNNImputer(n_neighbors=k)
        data_filled = pd.DataFrame(imputer.fit_transform(data_array), columns=data.columns, index=data.index)
    except Exception as e:
        print ("Error: No imputation occurred with error message {}".format(e));
        data_filled = data

    return data_filled