import os
import sys
import json
import time
import socket
import uuid
import random
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from utils import get_current_time
from config import _logger


def acked(err, msg):
    if err is not None:
        _logger.error("Failed to deliver message: %s: %s" % (str(msg.value()), str(err)))
    else:
        _logger.info("Message produced: %s" % (str(msg.value())))

def create_topic(conf, topic_name):
    kafka_admin = AdminClient(conf)
    # check if topic already exists, if not then create
    topic_metadata = kafka_admin.list_topics()
    if topic_metadata.topics.get(topic_name) is None:
        new_topic   = NewTopic(topic_name, 1, 1)
                # Number-of-partitions  = 1
                # Number-of-replicas    = 1
        kafka_admin.create_topics([new_topic,]) # CREATE (a list(), so you can create multiple).

def main():
    
    topic = os.environ['PRODUCER_KAFKA_TOPIC']
    p_key = str(uuid.uuid4())

    sensor_name = 'sensor_1'


    # my-release-kafka.default.svc.cluster.local
    conf = {'bootstrap.servers': "my-release-kafka.default.svc.cluster.local",
            'client.id': socket.gethostname()}
    producer = Producer(conf)

    # create topic if it does not exist
    create_topic(conf=conf, topic_name=topic)


    while True:
        time.sleep(10) #sleeping for some time interval
        try:

            result = {}
            # get current time
            timestamp = get_current_time()
            result[timestamp] = {'value': random.random(), 'sensor': sensor_name}
            # Convert dict to json as message format
            jresult = json.dumps(result).encode('utf-8')

            producer.produce(topic, jresult, timestamp, callback=acked)

            _logger.info('message published')
        # except TypeError:
        except TypeError as error:
            _logger.exception(str(error))
            sys.exit()
    
    producer.flush()


if __name__ == "__main__":
    main()