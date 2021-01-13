from tensorflow import keras
import numpy as np


class TimeSeriesPredict:
    def __init__(self, local=1):
        if local == 1:
            self.model = keras.models.load_model('../notebooks/lstm_model.h5')
        else:
            self.model = keras.models.load_model('notebooks/lstm_model.h5')
        self.shape = (1, 10, 1)
        self.last_input = np.array([[1, 0, 1] + [0] * 7]).reshape(1, 10, 1)

    def data_prepare(self, my_input):
        return np.array([my_input]).reshape(*self.shape)

    def get_output(self, last_input):
        raw_prediction = self.model.predict(self.data_prepare(last_input))
        prediction = list(raw_prediction[0])
        return [round(i) for i in prediction]

# a = TimeSeriesPredict().get_output([0] * 10)
# print(a)
