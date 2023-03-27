import configparser
import json
import random
from json import JSONEncoder

import numpy as np
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.utils import to_categorical

import utils


def load_dataset():
    (X_train, Y_train), (X_test, Y_test) = cifar10.load_data()
    X_train = X_train.astype("float32")
    X_test = X_test.astype("float32")
    X_train = X_train / 255.0
    X_test = X_test / 255.0
    Y_train = to_categorical(Y_train)
    Y_test = to_categorical(Y_test)
    return (X_train, Y_train), (X_test, Y_test)


def sampling_data(num_samples):
    (x_train, y_train), (x_test, y_test) = load_dataset()
    print(len(x_train))
    num_of_each_dataset = num_samples
    print(num_of_each_dataset)
    split_data_index = []
    while len(split_data_index) < num_of_each_dataset:
        item = random.choice(range(x_train.shape[0]))
        if item not in split_data_index:
            split_data_index.append(item)
    new_x_train = np.asarray([x_train[k] for k in split_data_index])
    new_y_train = np.asarray([y_train[k] for k in split_data_index])
    return new_x_train, new_y_train


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


class Trainer:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("../config.ini")
        self.num_samples = int(config["TRAINING"]["NUM_SAMPLES"])
        self.local_batch_size = int(config["TRAINING"]["LOCAL_BATCH_SIZE"])
        self.local_epochs = int(config["TRAINING"]["LOCAL_EPOCHS"])

    def train(self, queue_name, model_weights, global_epoch):
        model = utils.model_init()
        model_weights = json.loads(model_weights)
        model_weights = np.asarray(model_weights, dtype=object)
        model = utils.load_weights(model, model_weights)
        model.save_weights(
            f"trainer_storage/aggregator_models/{queue_name}_ep{global_epoch}.h5"
        )
        x_train, y_train = sampling_data(self.num_samples)
        model.compile(
            optimizer="sgd", loss="categorical_crossentropy", metrics=["accuracy"]
        )
        model.fit(
            x_train,
            y_train,
            epochs=self.local_epochs,
            batch_size=self.local_batch_size,
            verbose=1,
            validation_split=0.2,
        )
        model.save_weights(
            f"trainer_storage/trainer_models/{queue_name}_ep{global_epoch}.h5"
        )
        model_weights = model.get_weights()

        return model_weights
