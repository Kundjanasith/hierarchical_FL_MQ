from learning.tasks import celery_aggregate, celery_train
from learning.exchanger import Exchanger
from celery import Celery
import configparser
import json

config = configparser.ConfigParser()
config.read("../config.ini")

NUM_AGGREGATORS = int(config["DISTRIBUTION"]["NUM_AGGREGATORS"])
NUM_TRAINERS = json.loads(config["DISTRIBUTION"]["NUM_TRAINERS"])
NUM_COMMUNICATION_ROUNDS = int(config["TRAINING"]["NUM_COMMUNICATION_ROUNDS"])

def main():
    print(NUM_AGGREGATORS,type(NUM_AGGREGATORS))
    print(NUM_TRAINERS)
    
    list_global_models = {}
    for r in range(NUM_COMMUNICATION_ROUNDS):
        print('ROUND',r)
        exc = Exchanger()
        exchanged_model = exc.aggregate(list_global_models=list_global_models, global_epoch=r)

        list_local_models = {}
        result_list = []
        for a in range(1,NUM_AGGREGATORS+1):
            res = celery_aggregate.apply_async(kwargs={"list_local_models": list_local_models, "global_epoch": r, "exchanged_model": exchanged_model, "queue_name": f'aggregator{a}', "direction": "downlink"}, queue = f'aggregator{a}')
            result_list.append(res)

        trainer_result_list = {}
        for idx in range(1,NUM_AGGREGATORS+1):
            aggregated_model = result_list[idx-1].get(propagate=False)
            for t in range(1,NUM_TRAINERS[idx-1]+1):
                res = celery_train.apply_async(kwargs={"global_model": aggregated_model, "global_epoch": r, "queue_name": f'aggregator{idx}trainer{t}'},queue=f'aggregator{idx}trainer{t}')
                trainer_result_list[f'aggregator{idx}trainer{t}'] = res

        aggregator_result_list = []
        for idx in range(1,NUM_AGGREGATORS+1):
            list_local_models = {}
            for t in range(1,NUM_TRAINERS[idx-1]+1):
                list_local_models[f'aggregator{idx}trainer{t}'] = trainer_result_list[f'aggregator{idx}trainer{t}'].get(propagate=False)
            res = celery_aggregate.apply_async(kwargs={"list_local_models": list_local_models, "global_epoch": r, "exchanged_model": exchanged_model, "queue_name": f'aggregator{a}', "direction": "uplink"}, queue = f'aggregator{a}')
            aggregator_result_list.append(list)

        for idx in range(1,NUM_AGGREGATORS+1):
            list_global_models[f'aggregator{idx}'] = aggregator_result_list[idx-1].get(propagate=False)
        



    #     result_list = []
    #     for idx in range(1,NUM_TRAINERS+1):
    #         res = celery_train.apply_async(kwargs={"global_model": aggregated_model, "global_epoch": r, "queue_name": f'trainer{idx}'},queue=f'trainer{idx}')
    #         result_list.append(res)
    #     for idx in range(1,NUM_TRAINERS+1):
    #         list_local_models[f'trainer{idx}'] = result_list[idx-1].get(propagate=False)


            
        # res1 = celery_train.apply_async(kwargs={"global_model": aggregated_model, "global_epoch": r, "queue_name": 'trainer1'},queue='trainer1')
        # res2 = celery_train.apply_async(kwargs={"global_model": aggregated_model, "global_epoch": r, "queue_name": 'trainer2'},queue='trainer2')
        # list_local_models['trainer1'] = res1.get(propagate=False)
        # list_local_models['trainer2'] = res2.get(propagate=False)



if __name__ == "__main__":
    main()
