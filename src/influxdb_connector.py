from confluent_kafka import Consumer, KafkaError
import yaml
import yaml
import logging
import json
from influxdb import InfluxDBClient


# Your code here

def load_config():
    """
    Load configuration from a YAML file.

    Returns:
        dict: Configuration values.
    """
    with open("config/config.yaml", "r") as yamlfile:
        return yaml.safe_load(yamlfile)

config = load_config()

# Set up logging using config value
level = getattr(logging, config['logging']['level'].upper())
logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

def adjust_quotes(data):
    """Recursively modify values of dictionary to replace "'...'" with '...'"""
    if isinstance(data, dict):
        return {k: adjust_quotes(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [adjust_quotes(v) for v in data]
    elif isinstance(data, str) and data.startswith("'") and data.endswith("'"):
        return data[1:-1]
    else:
        return data

def save_event_in_db(event):
    client = InfluxDBClient(host=config['influxdb']['host'], port=config['influxdb']['port'], database=config['influxdb']['database'])
    client.create_database(config['influxdb']['database'])  # Can be removed if your database is already created
    flattened_event = flatten_json(event)
    tags = {
        "domain": event["event"]["commonEventHeader"]["domain"],
        "eventName": event["event"]["commonEventHeader"]["eventName"],
        "source": event["event"]["commonEventHeader"]["sourceName"],
        # Add any other tags you consider vital for your use case
    }
    if "measurementsForVfScalingFields" in event["event"] and "additionalObjects" in event["event"]["measurementsForVfScalingFields"] and len(event["event"]["measurementsForVfScalingFields"]["additionalObjects"]) > 0 and "objectName" in event["event"]["measurementsForVfScalingFields"]["additionalObjects"][0]:
        tags["objectName"] = event["event"]["measurementsForVfScalingFields"]["additionalObjects"][0]["objectName"]
    json_body = [{
        "measurement": event["event"]["commonEventHeader"]["domain"],
        "tags": tags,
        "time": event["event"]["commonEventHeader"]["lastEpochMicrosec"],
        "fields": flattened_event
    }]
    logger.debug(f"Saving event in database: {json_body}")
    client.write_points(json_body)
    client.close()


def get_kafka_config():
    return {
        'bootstrap.servers': f"{config['kafka']['bootstrap_servers']}:{config['kafka']['port']}",
        'group.id': config['kafka']['group_id'],
        'client.id': config['kafka']['client_id'],
        'enable.auto.commit': config['kafka']['enable_auto_commit'],
        'auto.offset.reset': config['kafka']['auto_offset_reset'],
    }

if __name__ == "__main__":
    consumer = Consumer(get_kafka_config())
    
    logger.info(f"Kafka consumer subscribing to topic(s): {config['kafka']['topics']}")
    consumer.subscribe(topics=config["kafka"]["topics"])

    try:
        while True:
            msg = consumer.poll(config['kafka']['poll_timeout_seconds'])
            logger.debug(f'Polling kafka topic {msg}')
            
            if msg is None:
                continue
            elif not msg.error():
                if msg.value() is None:
                    logger.warning("Received invalid message with None value.")
                    continue
                logger.debug(f'Received message from topic {msg.topic()} at offset {msg.offset()}')
                try:
                    msg_value = adjust_quotes(json.loads(msg.value().decode('utf-8')))
                    save_event_in_db(msg_value)
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode message: {msg.value().decode('utf-8')}")
            elif msg.error().code() == KafkaError._PARTITION_EOF:
                logger.error(f'End of partition reached {msg.topic()}/{msg.partition()}')
            else:
                logger.error(f'Error occurred: {msg.error().str()}')
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
