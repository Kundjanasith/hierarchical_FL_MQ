# conventional_FL_MQ

```
docker pull rabbitmq:management
```
```
docker run --rm -d -p 15671:15671/tcp -p 15672:15672/tcp -p 15691:15691/tcp -p 15692:15692/tcp -p 25672:25672/tcp -p 4369:4369/tcp -p 5671:5671/tcp -p 5672:5672/tcp rabbitmq:management
```
```
rabbitmqctl add_user myuser mypassword
rabbitmqctl add_vhost myvhost
rabbitmqctl set_user_tags myuser mytag
rabbitmqctl set_permissions -p myvhost myuser ".*" ".*" ".*"
```

celery -A my_celery_app worker --without-heartbeat --without-gossip --without-mingle

```
celery -A learning.tasks worker --without-heartbeat --without-gossip --without-mingle --loglevel=INFO -Q aggregator --concurrency=1 -n aggregator@%h
celery -A learning.tasks worker --without-heartbeat --without-gossip --without-mingle --loglevel=INFO -Q trainer1 --concurrency=1 -n trainer1@%h
celery -A learning.tasks worker --without-heartbeat --without-gossip --without-mingle --loglevel=INFO -Q trainer2 --concurrency=1 -n trainer2@%h
celery -A learning.tasks worker --without-heartbeat --without-gossip --without-mingle --loglevel=INFO -Q trainer3 --concurrency=1 -n trainer3@%h
celery -A learning.tasks worker --without-heartbeat --without-gossip --without-mingle --loglevel=INFO -Q trainer4 --concurrency=1 -n trainer4@%h
python3 start_training.py
```