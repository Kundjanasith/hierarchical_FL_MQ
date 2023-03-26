import utils, glob 
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.utils import to_categorical
import configparser
config = configparser.ConfigParser()
config.read("../config.ini")


def load_dataset():
    (X_train, Y_train), (X_test, Y_test) = cifar10.load_data()
    X_train = X_train.astype("float32")
    X_test = X_test.astype("float32")
    X_train = X_train / 255.0
    X_test = X_test / 255.0
    Y_train = to_categorical(Y_train)
    Y_test = to_categorical(Y_test)
    return (X_train, Y_train), (X_test, Y_test)

def calculate_loss_acccuracy(path):
    model = utils.model_init()
    model.load_weights(path)
    (X_train, Y_train), (X_test, Y_test) = load_dataset()
    model.compile(optimizer="sgd", loss="categorical_crossentropy", metrics=["accuracy"])
    loss, acc = model.evaluate(X_test, Y_test)
    return loss, acc

NUM_CLIENTS  = int(config["DISTRIBUTION"]["NUM_TRAINERS"])
# NUM_GLOBAL_EPOCH = int(config["TRAINING"]["NUM_COMMUNICATION_ROUNDS"])
NUM_GLOBAL_EPOCH = 35

# AGGREGATOR STORAGE

file_o = open('evaluation/aggregator.csv','w')
file_o.write(f'ep,loss,accuracy\n')
for e in range(NUM_GLOBAL_EPOCH):
    loss, acc = calculate_loss_acccuracy(f'aggregator_storage/aggregator_models/model_ep{e}.h5')
    file_o.write(f'{e},{loss},{acc}\n')
file_o.close()

for c in range(1,NUM_CLIENTS+1):
    file_o = open(f'evaluation/trainer{c}.csv','w')
    file_o.write(f'ep,loss,accuracy\n')
    for e in range(1,NUM_GLOBAL_EPOCH):
        loss, acc = calculate_loss_acccuracy(f'aggregator_storage/trainer_models/trainer{c}_ep{e}.h5')
        file_o.write(f'{e},{loss},{acc}\n')
    file_o.close()
