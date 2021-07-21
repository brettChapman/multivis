import pandas as pd
from sklearn.impute import KNNImputer

def imputeData(data, k=3):
    """Imputes data using K-nearest neighbours function, with a try-except for any errors
        Parameters
        ----------
        data : A pandas dataframe of values
        k : The number of nearest neighbours

        Returns
        -------
        data_filled : Imputed data
    """

    try:
        data_array = data.select_dtypes(include=float).values
        imputer = KNNImputer(n_neighbors=k)
        data_filled = pd.DataFrame(imputer.fit_transform(data_array), columns=data.columns, index=data.index)
    except Exception as e:
        print ("Error: No imputation occurred with error message {}".format(e));
        data_filled = data

    return data_filled