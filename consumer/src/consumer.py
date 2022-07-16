import os
import sys
import time
import json
import socket
from confluent_kafka import Producer, Consumer, KafkaError, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
from config import _logger
from utils import inc_analytics, get_current_time


def producer_acked(err, msg):
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
    _logger.info('starting consumer')
    conf = {'bootstrap.servers': "my-release-kafka.default.svc.cluster.local",
            'auto.offset.reset': 'smallest',
            'group.id': 'mygroup',
            'client.id': socket.gethostname()}

    consumer = Consumer(conf)
    producer = Producer(conf)

    running = True
    consumer.subscribe([os.environ['CONSUMER_KAFKA_TOPIC']])
    
    while running:

        msg = consumer.poll(1.0)
        if msg is None:
            _logger.info('Message is None')
            continue

        if msg.error():
            _logger.info('Message error')
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                    (msg.topic(), msg.partition(), msg.offset()))
            elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                sys.stderr.write('Topic unknown, creating %s topic\n' %
                                    ('mytopic'))
            elif msg.error():
                raise KafkaException(msg.error())
        else:
            _logger.info(msg.value())
            message_dict = json.loads(msg.value().decode('utf-8'))
            sensor_data = next(iter(message_dict.values()))
            sensor_key = str(sensor_data.get('sensor', 'default_sensor'))
            new_value_to_update = float(sensor_data.get('value', 0))
            updated_data = inc_analytics.update(sensor_key=sensor_key, new_value=new_value_to_update)
            _logger.info(updated_data)

            # produce the new value to the output channel
            if isinstance(updated_data, dict) and updated_data != {}:
                try:
                    # produce the value to the frontend channel
                    # create topic if it does not exist
                    create_topic(conf=conf, topic_name=os.environ['FRONTEND_PRODUCER_KAFKA_TOPIC'])
                    # produce to topic

                    # get current time
                    timestamp = get_current_time()
                    
                    # Convert dict to json as message format
                    updated_data_json = json.dumps(updated_data).encode('utf-8')
                    
                    producer.produce(os.environ['FRONTEND_PRODUCER_KAFKA_TOPIC'], updated_data_json, timestamp, callback=producer_acked)
                except Exception as e:
                    _logger.exception(str(e))


    # flush the producer
    producer.flush()

    # Close down consumer to commit final offsets.
    consumer.close()


if __name__ == "__main__":
    main()