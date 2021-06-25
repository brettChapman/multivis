import sys
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import MaxAbsScaler
from sklearn.preprocessing import RobustScaler
import pandas as pd
import numpy as np

def scaler(data, type="standard", newMin=1, newMax=10):
    """Scales a series of values in a 1D numpy array or pandas dataframe matrix based on different scaling functions

        Parameters
        ----------
        data : A pandas dataframe matrix or 1D numpy array of numerical values
        type : The scaler type to apply based on sklearn preprocessing functions (default: "standard")
        newMin : The minimum value for scaling (default: 1)
        newMax : The maximum value for scaling (default: 10)

        Returns
        -------
        scaled_data : A scaled pandas dataframe matrix or 1D numpy array of numerical values
    """

    data, type, newMin, newMax = __checkData(data, type, newMin, newMax)

    if isinstance(data, np.ndarray):
        data = data.reshape((data.shape[0], 1)).astype(float)

    if type.lower() == "standard":
        scaler = StandardScaler()
    elif type.lower() == "minmax":
        scaler = MinMaxScaler(feature_range=(newMin,newMax))
    elif type.lower() == "maxabs":
        scaler = MaxAbsScaler()
    elif type.lower() == "robust":
        scaler = RobustScaler(quantile_range=(newMin,newMax))

    if isinstance(data, np.ndarray):
        scaled_data = scaler.fit_transform(data).flatten()
    elif isinstance(data, pd.DataFrame):
        scaled_data = scaler.fit_transform(data)

    if isinstance(data, pd.DataFrame):
        scaled_data = pd.DataFrame(scaled_data, columns=data.columns, index=data.index)
                    
    return scaled_data

def __checkData(data, type, newMin, newMax):

    if not isinstance(data, pd.DataFrame):
        if not isinstance(data, np.ndarray):
            print("Error: A pandas dataframe or numpy array was not entered. Please check your data.")
            sys.exit()

    if type.lower() not in ["standard", "minmax", "maxabs", "robust"]:
        print("Error: Scaler type not valid. Choose either \"Standard\", \"MinMax\", \"MaxAbs\", or \"Robust\".")
        sys.exit()

    if not isinstance(newMin, float):
        if not isinstance(newMin, int):
            print("Error: The minimum value is not valid. Choose a float or integer value.")
            sys.exit()

    if not isinstance(newMax, float):
        if not isinstance(newMax, int):
            print("Error: The maximum value is not valid. Choose a float or integer value.")
            sys.exit()

    return data, type, newMin, newMax