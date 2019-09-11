from sklearn.preprocessing import MinMaxScaler
import numpy as np

def range_scale(data, newMin, newMax):
    """Scales a series of values between a minimum and maximum value

        Parameters
        ----------
        data : A numpy array of values

        newMin : The minimum value to scale the numpy array to

        newMax : The maximum value to scale the number array to

        Returns
        -------
        scaled_data : A scaled numpy array
    """

    data = data.reshape((data.shape[0], 1)).astype(float)
    scaler = MinMaxScaler(feature_range=(newMin,newMax))
    
    scaled_data = scaler.fit_transform(data).flatten()
                    
    return scaled_data