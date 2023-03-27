# hierarchical_FL_MQ

## Setup RabbitMQ

```
docker run --rm -d -p 15671:15671/tcp -p 15672:15672/tcp -p 15691:15691/tcp -p 15692:15692/tcp -p 25672:25672/tcp -p 4369:4369/tcp -p 5671:5671/tcp -p 5672:5672/tcp rabbitmq:management
```

### Execute the following command in RabbitMQ container
```
rabbitmqctl add_user myuser mypassword
rabbitmqctl add_vhost myvhost
rabbitmqctl set_user_tags myuser mytag
rabbitmqctl set_permissions -p myvhost myuser ".*" ".*" ".*"
```

## Setup Federated learning

```
git clone ttps://github.com/Kundjanasith/hierarchical_FL_MQ
cd src
```

### Execute the following command in trainer node {x} of aggregator node {y}
```
celery -A learning.tasks worker --without-heartbeat --without-gossip --without-mingle --loglevel=INFO -Q aggregator{y}trainer{x} --concurrency=1 -n aggregator{y}trainer{x}@%h
```

### Execute the following command in aggregator node {y}
```
celery -A learning.tasks worker --without-heartbeat --without-gossip --without-mingle --loglevel=INFO -Q aggregator{y} --concurrency=1 -n aggregator{y}@%h
```

### Execute the following commaind in exchanger node
```
python3 start_training.py
```