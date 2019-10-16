from sklearn.preprocessing import MinMaxScaler
import numpy as np

def range_scale(data, newMin, newMax):
    """Scales a series of values in a numpy array between a minimum and maximum value

        Parameters
        ----------
        data : A 1D numpy array of values
        newMin : The minimum value to scale the numpy array to
        newMax : The maximum value to scale the number array to

        Returns
        -------
        scaled_data : A scaled numpy array
    """

    data, newMin, newMax = __checkData(data, newMin, newMax)

    data = data.reshape((data.shape[0], 1)).astype(float)
    scaler = MinMaxScaler(feature_range=(newMin,newMax))
    
    scaled_data = scaler.fit_transform(data).flatten()
                    
    return scaled_data

def __checkData(data, newMin, newMax):

    if not isinstance(data, np.ndarray):
        print("Error: A numpy array was not entered. Please check your data.")
        sys.exit()

    if not isinstance(newMin, float):
        if not isinstance(newMin, int):
            print("Error: The minimum value is not valid. Choose a float or integer value.")
            sys.exit()

    if not isinstance(newMax, float):
        if not isinstance(newMax, int):
            print("Error: The maximum value is not valid. Choose a float or integer value.")
            sys.exit()

    return data, newMin, newMax