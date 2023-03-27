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
    # for r in range(3):
        print('ROUND',r)
        exc = Exchanger()
        exchanged_model = exc.aggregate(list_global_models=list_global_models, global_epoch=r)

        local_model = None
        result_list = []
        for a in range(1,NUM_AGGREGATORS+1):
            res = celery_aggregate.apply_async(kwargs={"local_model": local_model, "global_epoch": r, "exchanged_model": exchanged_model, "queue_name": f'aggregator{a}', "direction": "downlink"}, queue = f'aggregator{a}')
            result_list.append(res)

        trainer_result_list = {}
        for idx in range(1,NUM_AGGREGATORS+1):
            aggregated_model = result_list[idx-1].get(propagate=False)
            for t in range(1,NUM_TRAINERS[idx-1]+1):
                res = celery_train.apply_async(kwargs={"global_model": aggregated_model, "global_epoch": r, "queue_name": f'aggregator{idx}trainer{t}'},queue=f'aggregator{idx}trainer{t}')
                trainer_result_list[f'aggregator{idx}trainer{t}'] = res

        aggregator_result_list = {}
        exchanged_model = None
        for idx in range(1,NUM_AGGREGATORS+1):
            list_local_models = {}
            for t in range(1,NUM_TRAINERS[idx-1]+1):
                local_model = trainer_result_list[f'aggregator{idx}trainer{t}'].get(propagate=False)
                res = celery_aggregate.apply_async(kwargs={"local_model": local_model, "global_epoch": r, "exchanged_model": exchanged_model, "queue_name": f'aggregator{idx}trainer{t}', "direction": "uplink"}, queue = f'aggregator{a}')
                print(f'aggregator{idx}trainer{t}')
                aggregator_result_list[f'aggregator{idx}trainer{t}'] = res
        
        print('start cal')
        for idx in range(1,NUM_AGGREGATORS+1):
            for t in range(1,NUM_TRAINERS[idx-1]+1):
                print(f'aggregator{idx}trainer{t}')
                res = aggregator_result_list[f'aggregator{idx}trainer{t}'].get(propagate=False)
                # print(res)
                if res != None:
                    list_global_models[f'aggregator{idx}'] = res
        
        print(list_global_models.keys())
        for i in list_global_models.keys():
            print(type(list_global_models[i]))


if __name__ == "__main__":
    main()
