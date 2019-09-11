from sklearn.preprocessing import MinMaxScaler
import numpy as np

def range_scale(x, newMin, newMax):
    """Scales a series of values between a minimum and maximum value

        Parameters
        ----------
        x : A numpy array of values

        newMin : The minimum value to scale the numpy array to

        newMax : The maximum value to scale the number array to

        Returns
        -------
        scaled_x : A scaled numpy array
    """

    x = x.reshape((x.shape[0], 1)).astype(float)
    scaler = MinMaxScaler(feature_range=(newMin,newMax))
    
    scaled_x = scaler.fit_transform(x).flatten()   
                    
    return scaled_x