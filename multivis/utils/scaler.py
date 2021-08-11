import sys
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import MaxAbsScaler
from sklearn.preprocessing import RobustScaler
import pandas as pd
import numpy as np

def scaler(data, type="standard", stdScaler_with_mean=True, stdScaler_with_std=True, robust_with_centering=True, robust_with_scaling=True, robust_unit_variance=False, minimum=0, maximum=1, lower_iqr=25.0, upper_iqr=75.0):
    """Scales a series of values in a 1D numpy array or pandas dataframe matrix based on different scaling functions

        Parameters
        ----------
        data: A pandas dataframe matrix or 1D numpy array of numerical values
        type: The scaler type to apply based on sklearn preprocessing functions (default: "standard")
        stdScaler_with_mean: Using "standard" scaler, center the data to the mean before scaling (default: True)
        stdScaler_with_std: Using "standard" scaler, scale the data to unit variance (default: True)
        robust_with_centering: Using "robust" scaler, center the data to the median before scaling (default: True)
        robust_with_scaling: Using "robust" scaler, scale the data to within the quantile range (default: True)
        robust_unit_variance: Using "robust" scaler, scale the data so that normally distributed features have a variance of 1 (default: False)
        minimum: Using "minmax" scaler, set the minimum value for scaling (default: 0)
        maximum: Using "minmax" scaler, set the maximum value for scaling (default: 1)
        lower_iqr: Using "robust" scaler, set the lower quantile range (default: 25.0)
        upper_iqr: Using "robust" scaler, set the upper quantile range (default: 75.0)

        Returns
        -------
        scaled_data: A scaled pandas dataframe matrix or 1D numpy array of numerical values
    """

    data, type, stdScaler_with_mean, stdScaler_with_std, robust_with_centering, robust_with_scaling, robust_unit_variance, minimum, maximum, lower_iqr, upper_iqr = __checkData(data, type, stdScaler_with_mean, stdScaler_with_std, robust_with_centering, robust_with_scaling, robust_unit_variance, minimum, maximum, lower_iqr, upper_iqr)

    if isinstance(data, np.ndarray):
        data = data.reshape((data.shape[0], 1)).astype(float)

    if type.lower() == "standard":
        scaler = StandardScaler(with_mean=stdScaler_with_mean, with_std=stdScaler_with_std)
    elif type.lower() == "minmax":
        scaler = MinMaxScaler(feature_range=(minimum,maximum))
    elif type.lower() == "maxabs":
        scaler = MaxAbsScaler()
    elif type.lower() == "robust":
        scaler = RobustScaler(with_centering=robust_with_centering, with_scaling=robust_with_scaling, unit_variance=robust_unit_variance, quantile_range=(lower_iqr,upper_iqr))

    if isinstance(data, np.ndarray):
        scaled_data = scaler.fit_transform(data).flatten()
    elif isinstance(data, pd.DataFrame):
        scaled_data = scaler.fit_transform(data)

    if isinstance(data, pd.DataFrame):
        scaled_data = pd.DataFrame(scaled_data, columns=data.columns, index=data.index)
                    
    return scaled_data

def __checkData(data, type, stdScaler_with_mean, stdScaler_with_std, robust_with_centering, robust_with_scaling, robust_unit_variance, minimum, maximum, lower_iqr, upper_iqr):

    if not isinstance(data, pd.DataFrame):
        if not isinstance(data, np.ndarray):
            print("Error: A pandas dataframe or numpy array was not entered. Please check your data.")
            sys.exit()

    if type.lower() not in ["standard", "minmax", "maxabs", "robust"]:
        print("Error: Scaler type not valid. Choose either \"Standard\", \"MinMax\", \"MaxAbs\", or \"Robust\".")
        sys.exit()

    if not isinstance(stdScaler_with_mean, bool):
        print("Error: The standard scaler with mean value is not valid. Choose either \"True\" or \"False\".")
        sys.exit()

    if not isinstance(stdScaler_with_std, bool):
        print("Error: The standard scaler with standard deviation (unit variance) value is not valid. Choose either \"True\" or \"False\".")
        sys.exit()

    if not isinstance(robust_with_centering, bool):
        print("Error: The robust scaler with centering value is not valid. Choose either \"True\" or \"False\".")
        sys.exit()

    if not isinstance(robust_with_scaling, bool):
        print("Error: The robust scaler with scaling value is not valid. Choose either \"True\" or \"False\".")
        sys.exit()

    if not isinstance(robust_unit_variance, bool):
        print("Error: The robust scaler with unit variance value is not valid. Choose either \"True\" or \"False\".")
        sys.exit()

    if not isinstance(minimum, float):
        if not isinstance(maximum, int):
            print("Error: The minmax scaler minimum value is not valid. Choose a float or integer value.")
            sys.exit()

    if not isinstance(maximum, float):
        if not isinstance(maximum, int):
            print("Error: The minmax scaler maximum value is not valid. Choose a float or integer value.")
            sys.exit()

    if not isinstance(lower_iqr, float):
        if not isinstance(lower_iqr, int):
            print("Error: The robust lower interquartile range value is not valid. Choose a float or integer value.")
            sys.exit()

    if not isinstance(upper_iqr, float):
        if not isinstance(upper_iqr, int):
            print("Error: The robust upper interquartile range value is not valid. Choose a float or integer value.")
            sys.exit()

    return data, type, stdScaler_with_mean, stdScaler_with_std, robust_with_centering, robust_with_scaling, robust_unit_variance, minimum, maximum, lower_iqr, upper_iqr