import configparser

from celery import Celery

config = configparser.ConfigParser()
config.read("../config.ini")

PYAMQP_IP = config["DISTRIBUTION"]["PYAMQP_IP"]
NUM_TRAINERS = int(config["DISTRIBUTION"]["NUM_TRAINERS"])

def task_routes_init() -> dict:
    result = {}
    result["learning.tasks.celery_aggregate"] = {"queue": "aggregator"}
    trainers_bound = NUM_TRAINERS + 1
    for idx in range(1, trainers_bound):
        result["learning.tasks.celery_train"] = {"queue": f"trainer{idx}"}
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
