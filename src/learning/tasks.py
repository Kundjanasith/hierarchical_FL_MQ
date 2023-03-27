import json, utils
import numpy as np 
import glob
from celery.signals import celeryd_after_setup

from app import app
from learning.aggregator import Aggregator
# from learning.config import CONFIG
import configparser
from learning.trainer import Trainer

config = configparser.ConfigParser()
config.read("../config.ini")

NUM_TRAINERS = json.loads(config["DISTRIBUTION"]["NUM_TRAINERS"])


# @celeryd_after_setup.connect
# def capture_worker_name(sender, headers=None, body=None, **kwargs):
#     sender_name = str(sender).split("@")[0]
#     print(f"sender: {sender}, sender_name: {sender_name}")
#     CONFIG["sender_name"] = sender_name

@app.task()
def celery_aggregate(local_model, global_epoch: int, exchanged_model, queue_name: str, direction: str) -> None:
    if direction == "downlink":
        model = utils.model_init()
        model_weights = json.loads(exchanged_model)
        model_weights = np.asarray(model_weights, dtype=object)
        model = utils.load_weights(model, model_weights)
        model.save_weights(f"aggregator_storage/exchanger_models/model_ep{global_epoch}.h5")
        return exchanged_model
    else:
        print(direction)
        model = utils.model_init()
        print(1)
        model_weights = json.loads(local_model)
        print(2)
        model_weights = np.asarray(model_weights, dtype=object)
        print(3)
        model = utils.load_weights(model, model_weights)
        print(4)
        model.save_weights(f"aggregator_storage/trainer_models/{queue_name}_ep{global_epoch}.h5")
        # return model
        aggregator_idx = int(queue_name.split('aggregator')[1].split('trainer')[0])
        print(aggregator_idx)
        print(NUM_TRAINERS[aggregator_idx-1] == len(glob.glob(f"aggregator_storage/trainer_models/aggregator{aggregator_idx}trainer*_ep{global_epoch}.h5")))
        print(NUM_TRAINERS[aggregator_idx-1],queue_name)
        print(len(glob.glob(f"aggregator_storage/trainer_models/aggregator{aggregator_idx}trainer*_ep{global_epoch}.h5")))
        if NUM_TRAINERS[aggregator_idx-1] == len(glob.glob(f"aggregator_storage/trainer_models/aggregator{aggregator_idx}trainer*_ep{global_epoch}.h5")):
            aggr = Aggregator()
            list_local_models = {}
            for i in range(1,NUM_TRAINERS[aggregator_idx-1]+1):
                model = utils.model_init()
                model.load_weights(f"aggregator_storage/trainer_models/aggregator{aggregator_idx}trainer{i}_ep{global_epoch}.h5")
                model_weights = model.get_weights()
                model_weights = json.dumps(model_weights, cls=utils.NumpyArrayEncoder)
                list_local_models[f'aggregator{aggregator_idx}trainer{i}'] = model_weights
            print(list_local_models.keys())
            aggregated_model = aggr.aggregate(list_local_models, global_epoch, aggregator_idx)
            return aggregated_model
        else:
            return None


# @app.task()
# def celery_store(exchanged_model, global_epoch: int, queue_name: str) -> None:
#     aggr = Aggregator()
#     print(list_local_models.keys())
#     aggregated_model = aggr.aggregate(list_local_models, global_epoch)
#     return aggregated_model

@app.task()
def celery_train(global_model, global_epoch: int, queue_name: str) -> None:
    trainer = Trainer()
    trained_model = trainer.train(queue_name, global_model, global_epoch)
    model_weights = json.dumps(trained_model, cls=utils.NumpyArrayEncoder)
    return model_weights