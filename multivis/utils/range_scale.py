from sklearn.preprocessing import MinMaxScaler
import numpy as np

def range_scale(x, newMin, newMax):
        
    x = x.reshape((x.shape[0], 1)).astype(float)
    scaler = MinMaxScaler(feature_range=(newMin,newMax))
    
    scaled_x = scaler.fit_transform(x).flatten()   
                    
    return scaled_x