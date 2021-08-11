import sys
from .scaler import scaler
from sklearn.preprocessing import OrdinalEncoder
import numpy as np

def transform(data, transform_type, min, max):
    """Scales and transforms data in forward or reverse order based on different transform options

        Parameters
        ----------
        data :  A 1D numpy array of values
        transform_type : The transform type to apply to the data ("linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume", "ordinal", "reverse_ordinal")
        min : The minimum value for scaling
        max : The maximum value for scaling

        Returns
        -------
        transformed_data : A scaled and transformed numpy array
    """

    data, transform_type, min, max = __checkData(data, transform_type, min, max)

    if transform_type != "ordinal":
        #if not ordinal scale first between 1 and 10 to avoid log zero and divide by zero errors while transforming
        data = np.array([x for x in list(scaler(data, type="minmax", minimum=1, maximum=10))])

    scaled_data = []
    if transform_type == 'linear':
        scaled_data = [x for x in list(scaler(data, type='minmax', minimum=min, maximum=max))]
    if transform_type == 'reverse_linear':
        data = np.divide(1, data)
        scaled_data = [x for x in list(scaler(data, type='minmax', minimum=min, maximum=max))]
    elif transform_type == 'log':
        data = np.log(data)
        scaled_data = [x for x in list(scaler(data, type='minmax', minimum=min, maximum=max))]
    elif transform_type == 'reverse_log':
        data = np.divide(1, data)
        data = np.log(data)
        scaled_data = [x for x in list(scaler(data, type='minmax', minimum=min, maximum=max))]
    elif transform_type == 'square':
        data = np.square(data)
        scaled_data = [x for x in list(scaler(data, type='minmax', minimum=min, maximum=max))]
    elif transform_type == 'reverse_square':
        data = np.divide(1, data)
        data = np.square(data)
        scaled_data = [x for x in list(scaler(data, type='minmax', minimum=min, maximum=max))]
    elif transform_type == 'area':
        data = np.square(data)
        data = [np.multiply(x, np.pi) for x in list(map(float, data))]
        scaled_data = [round(x) for x in list(map(int, scaler(data, type='minmax', minimum=min, maximum=max)))]
    elif transform_type == 'reverse_area':
        data = np.divide(1, data)
        data = np.square(data)
        data = [np.multiply(x, np.pi) for x in list(map(float, data))]
        scaled_data = [round(x) for x in list(map(int, scaler(data, type='minmax', minimum=min, maximum=max)))]
    elif transform_type == 'volume':
        data = [np.power(x, 3) for x in list(map(float, data))]
        data = [np.multiply(x, np.pi) for x in list(map(float, data))]
        data = [np.multiply(x, 4 / 3) for x in list(map(float, data))]
        scaled_data = [round(x) for x in list(map(int, scaler(data, type='minmax', minimum=min, maximum=max)))]
    elif transform_type == 'reverse_volume':
        data = np.divide(1, data)
        data = [np.power(x, 3) for x in list(map(float, data))]
        data = [np.multiply(x, np.pi) for x in list(map(float, data))]
        data = [np.multiply(x, 4 / 3) for x in list(map(float, data))]
        scaled_data = [round(x) for x in list(map(int, scaler(data, type='minmax', minimum=min, maximum=max)))]
    elif transform_type == 'ordinal':
        encoder = OrdinalEncoder()

        scaled_data = encoder.fit_transform(data.reshape(-1, 1)).flatten()

        scaled_data = np.array([x for x in list(scaler(scaled_data, type="minmax", minimum=min, maximum=max))])
    elif transform_type == 'reverse_ordinal':
        encoder = OrdinalEncoder()

        scaled_data = encoder.fit_transform(data.reshape(-1, 1)).flatten()

        scaled_data = np.divide(1, scaled_data)

        scaled_data = np.array([x for x in list(scaler(scaled_data, type="minmax", minimum=min, maximum=max))])

    return scaled_data

def __checkData(data, transform, min, max):

    if not isinstance(data, np.ndarray):
        print("Error: A numpy array was not entered. Please check your data.")
        sys.exit()

    if transform.lower() not in ["linear", "reverse_linear", "log", "reverse_log", "square", "reverse_square", "area", "reverse_area", "volume", "reverse_volume", "ordinal", "reverse_ordinal"]:
        print("Error: The chosen transform type is not valid. Choose either \"linear\", \"reverse_linear\", \"log\", \"reverse_log\", \"square\", \"reverse_square\", \"area\", \"reverse_area\", \"volume\", \"reverse_volume\", \"ordinal\", \"reverse_ordinal\".")
        sys.exit()

    if not isinstance(min, float):
        if not isinstance(min, int):
            print("Error: The minimum scaling value is not valid. Choose a float or integer value.")
            sys.exit()

    if not isinstance(max, float):
        if not isinstance(max, int):
            print("Error: The maximum scaling value is not valid. Choose a float or integer value.")
            sys.exit()

    return data, transform, min, max