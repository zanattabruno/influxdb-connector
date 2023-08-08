# Dockerfile

FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /app
COPY src/influxdb_connector.py .
CMD ["python", "influxdb_connector.py"]