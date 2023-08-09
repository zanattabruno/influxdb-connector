# InfluxDB Connector for Kafka
The InfluxDB Connector consumes messages from specified Kafka topics and saves them to InfluxDB after processing and flattening the nested JSON objects. This connector utilizes the confluent-kafka library for Kafka consumption and the InfluxDB client library for database operations.

## Features

- Configurable Kafka consumer that can subscribe to multiple topics.
- Flattens nested JSON objects for efficient storage in InfluxDB.
- Supports dynamic configuration via YAML files.
- Logs events for easier monitoring and debugging.

## Installation

1. Ensure you have Python 3.x installed.
2. Clone the GitHub repository:
```bash
git clone https://github.com/zanattabruno/influxdb-connector.git
cd influxdb-connector
```
3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Configuration
The application requires a configuration YAML file with settings for both Kafka and InfluxDB. You can find a template in 'config/config.yaml. Here's a brief overview of the configuration parameters:

### Kafka Configuration
- bootstrap_servers: The address of your Kafka cluster.
- port: The port number for the Kafka service.
- enable_auto_commit: Indicates whether to commit offsets automatically.
- auto_commit_interval_ms: Time interval for auto commit.
- auto_offset_reset: Specifies the strategy for offset resetting.
- group_id: Identifier for the Kafka consumer group.
- client_id: Identifier for the Kafka consumer client.
- poll_timeout_seconds: Timeout duration for Kafka poll.
- topics: List of topics to which the consumer should subscribe.## Key Functionalities

### InfluxDB Configuration
- host: The address of your InfluxDB service.
- port: The port number for the InfluxDB service.
- database: The name of the InfluxDB database to save events.

## Usage
1. Update the config/config.yaml file with the appropriate configuration for your setup.

```bash
pip install -r requirements.txt
```

Check the logs for any errors or issues, and monitor the InfluxDB database to ensure the messages are being saved.
## InfluxDB Connector Helm Installation
### Pre-requisites
Before starting the deployment, ensure you have the following:
- A running Kubernetes cluster.
- The kubectl and helm command-line tools properly set up and connected to your cluster.
- A Kafka broker and InfluxDB instance running within or accessible to the cluster. The InfluxDB Connector is designed to consume Kafka topics and save them to an InfluxDB database.

### values.yaml
```yaml
# Kafka configuration
kafka:
  bootstrap_servers: "kafka.smo.svc.cluster.local"
  port: 9092
  enable_auto_commit: true
  auto_commit_interval_ms: 6000
  auto_offset_reset: "earliest"
  group_id: "influxdb-connector"
  client_id: "influxdb-connector"
  poll_timeout_seconds: 1
  topics:
    - heartbeat
    - measurementsforvfscaling

# InfluxDB configuration
influxdb:
  host: "influxdb.smo.svc.cluster.local"
  port: 8086
  database: "smo"

# Logging configuration
logging:
  level: INFO

# Replica count
replicaCount: 1

# Docker image configuration
image:
  repository: zanattabruno/influxdb-connector
  pullPolicy: Always
  tag: "latest"


# Kubernetes pod configuration
podAnnotations: {}
podSecurityContext: {}
securityContext: {}
service:
  type: ClusterIP
  port: 80

# Kubernetes ingress configuration
ingress:
  enabled: false
  className: ""
  annotations: {}
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: ImplementationSpecific
  tls: []

# Kubernetes resource configuration
resources: {}
autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 100
  targetCPUUtilizationPercentage: 80
nodeSelector: {}
tolerations: []
affinity: {}
```

### Deploying the chart

For clarity and better organization, it's recommended to deploy this application in a separate namespace. Here, we'll use the namespace smo.

```bash
cd influxdb-connector
helm install influxdb-connector helm/influxdb-connector -n smo
```

### Monitoring and Usage

After deploying the Helm chart, the InfluxDB Connector should begin listening for messages from the configured Kafka topics and storing them in the specified InfluxDB database. Monitor the application's logs for any errors or issues, and validate the InfluxDB database to confirm the messages are correctly saved.





