import configparser
import json
from celery import Celery

config = configparser.ConfigParser()
config.read("../config.ini")

PYAMQP_IP = config["DISTRIBUTION"]["PYAMQP_IP"]
NUM_TRAINERS = json.loads(config["DISTRIBUTION"]["NUM_TRAINERS"])
NUM_AGGREGATORS = int(config["DISTRIBUTION"]["NUM_AGGREGATORS"])

def task_routes_init() -> dict:
    result = {}
    aggregators_bound = NUM_AGGREGATORS + 1
    for idx in range(1,aggregators_bound):
        result["learning.tasks.celery_aggregate"] = {"queue": f"aggregator{idx}"}
        for t in range(1,NUM_TRAINERS[idx-1]+1):
            result["learning.tasks.celery_train"] = {"queue": f"aggregator{idx}trainer{t}"}
    return result


app = Celery(
    "fedlearn",
    backend="rpc://",
    broker=f"pyamqp://myuser:mypassword@{PYAMQP_IP}:5672/myvhost",
    include=["learning.tasks"],
)

app.conf.update(
    result_expires=3600,
    task_routes=task_routes_init(),
)

if __name__ == "__main__":
    app.start()
