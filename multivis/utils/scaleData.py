import sys
from .scaler import scaler
from sklearn.preprocessing import OrdinalEncoder
import numpy as np

def scaleData(data, scale, min, max):
    """Scales data in forward or reverse order based on different scaling options

        Parameters
        ----------
        data : A 1D numpy array of values
        scale : The scaling option chosen to apply to the data
        min : The minimum value for scaling
        max : The maximum value for scaling

        Returns
        -------
        scaled_data : A scaled numpy array
    """

    data, scale, min, max = __checkData(data, scale, min, max)

    if scale != "ordinal":
        data = np.array([x for x in list(scaler(data, "minmax", 1, 10))])

    scaled_data = []
    if scale == 'linear':
        scaled_data = [x for x in list(scaler(data, 'minmax', min, max))]
    if scale == 'reverse_linear':
        data = np.divide(1, data)
        scaled_data = [x for x in list(scaler(data, 'minmax', min, max))]
    elif scale == 'log':
        data = np.log(data)
        scaled_data = [x for x in list(scaler(data, 'minmax', min, max))]
    elif scale == 'reverse_log':
        data = np.divide(1, data)
        data = np.log(data)
        scaled_data = [x for x in list(scaler(data, 'minmax', min, max))]
    elif scale == 'square':
        data = np.square(data)
        scaled_data = [x for x in list(scaler(data, 'minmax', min, max))]
    elif scale == 'reverse_square':
        data = np.divide(1, data)
        data = np.square(data)
        scaled_data = [x for x in list(scaler(data, 'minmax', min, max))]
    elif scale == 'area':
        data = np.square(data)
        data = [np.multiply(x, np.pi) for x in list(map(float, data))]
        scaled_data = [round(x) for x in list(map(int, scaler(data, 'minmax', min, max)))]
    elif scale == 'reverse_area':
        data = np.divide(1, data)
        data = np.square(data)
        data = [np.multiply(x, np.pi) for x in list(map(float, data))]
        scaled_data = [round(x) for x in list(map(int, scaler(data, 'minmax', min, max)))]
    elif scale == 'volume':
        data = [np.power(x, 3) for x in list(map(float, data))]
        data = [np.multiply(x, np.pi) for x in list(map(float, data))]
        data = [np.multiply(x, 4 / 3) for x in list(map(float, data))]
        scaled_data = [round(x) for x in list(map(int, scaler(data, 'minmax', min, max)))]
    elif scale == 'reverse_volume':
        data = np.divide(1, data)
        data = [np.power(x, 3) for x in list(map(float, data))]
        data = [np.multiply(x, np.pi) for x in list(map(float, data))]
        data = [np.multiply(x, 4 / 3) for x in list(map(float, data))]
        scaled_data = [round(x) for x in list(map(int, scaler(data, 'minmax', min, max)))]
    elif scale == 'ordinal':
        encoder = OrdinalEncoder()

        scaled_data = encoder.fit_transform(data.reshape(-1, 1)).flatten()

        scaled_data = np.array([x for x in list(scaler(scaled_data, "minmax", min, max))])

    return scaled_data

def __checkData(data, scale, min, max):

    if not isinstance(data, np.ndarray):
        print("Error: A numpy array was not entered. Please check your data.")
        sys.exit()

    if scale.lower() not in ["linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume", "ordinal"]:
        print("Error: Scale value not valid. Choose either \"linear\", \"reverse_linear\", \"log\", \"reverse_log\", \"square\", \"reverse_square\", \"area\", \"reverse_area\", \"volume\", \"reverse_volume\", \"ordinal\".")
        sys.exit()

    if not isinstance(min, float):
        if not isinstance(min, int):
            print("Error: The minimum value is not valid. Choose a float or integer value.")
            sys.exit()

    if not isinstance(max, float):
        if not isinstance(max, int):
            print("Error: The maximum value is not valid. Choose a float or integer value.")
            sys.exit()

    return data, scale, min, max