from json import JSONEncoder

import numpy as np
from tensorflow.keras import Model
from tensorflow.keras.applications.mobilenet import MobileNet
from tensorflow.keras.layers import BatchNormalization, Dense, Flatten, Input


def model_init():
    model = MobileNet(include_top=False, input_tensor=Input(shape=(32, 32, 3)))
    x = model.output
    x = Flatten()(x)
    x = Dense(512, activation="relu")(x)
    x = BatchNormalization()(x)
    x = Dense(10, activation="softmax")(x)
    model = Model(model.input, x)
    return model


def getLayerIndexByName(model, layername):
    for idx, layer in enumerate(model.layers):
        if layer.name == layername:
            return idx


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


def load_weights(model, model_weights):
    count = 0
    for i in model.layers:
        l_idx = getLayerIndexByName(model, i.name)
        if len(i.get_weights()) > 0:
            arr = []
            for j in range(len(i.get_weights())):
                arr.append(np.array(model_weights[count]))
                count = count + 1
            arr = np.array(arr, dtype=object)
            model.get_layer(index=l_idx).set_weights(arr)
    return model
