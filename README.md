# 🚀 Final Project: My First Monitoring System
A complete step-by-step guide to setting up a monitoring system using Flask, Prometheus, Grafana, ELK, and Alerting.

# 📌 What You'll Build
You'll create a monitoring system for a small web app (Cool Tech Store) to track:

✅ Website uptime

✅ Number of visitors

✅ Errors occurring

✅ Server health (CPU & Memory)

✅ Application logs

✅ Alerts via Slack/Email

# 📌 Step 1: Set Up Flask App
We'll create a Flask web app that logs visits and errors.

## 1️⃣ Create Project Directory
```
mkdir monitoring_project && cd monitoring_project
```
## 2️⃣ Create app.py
```
from flask import Flask
import random
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO)

@app.route('/')
def home():
    app.logger.info("Homepage visited")
    return "Welcome to Cool Tech Store!", 200

@app.route('/error')
def error():
    app.logger.error("An error occurred!")
    return "Something went wrong!", 500

@app.route('/health')
def health():
    return {"status": "healthy"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```
## 3️⃣ Create requirements.txt
```
flask
```
## 4️⃣ Test Flask Locally
```
pip install -r requirements.txt
python app.py
```
- Test in browser or terminal:
```
curl http://localhost:5000/
```
# 📌 Step 2: Containerize with Docker
## 1️⃣ Create Dockerfile
```
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```
## 2️⃣ Create docker-compose.yml
```
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
    networks:
      - monitoring

networks:
  monitoring:
```
## 3️⃣ Run Docker
```
docker-compose up --build
```
- Test:
```
curl http://localhost:5000/
```
# 📌 Step 3: Set Up Monitoring with Prometheus & Grafana
## 1️⃣ Add Prometheus to docker-compose.yml
```
 prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    networks:
      - monitoring
```
## 2️⃣ Create prometheus.yml
```
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: "flask_app"
    static_configs:
      - targets: ["web:5000"]
```
## 3️⃣ Add Grafana to docker-compose.yml
```
 grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    networks:
      - monitoring
```
## 4️⃣ Run Services
```
docker-compose up -d
```
- Prometheus: http://localhost:9090/
- Grafana: http://localhost:3000/ (user: admin, pass: admin)
## 5️⃣ Add Grafana Dashboard
- Open Grafana
- Add Prometheus as a Data Source
1. Click Configuration (⚙️) → Data Sources

2. Click "Add Data Source"

3. Select Prometheus

4. Set the URL to:
```
http://prometheus:9090
```
5. Click Save & Test

 You should see a green success message.

- Create a Dashboard
1. Click Dashboards (📊) → New Dashboard

2. Click "Add New Panel"

3. In the Query box, enter:
```
http_requests_total
```
4. Click Run Query

5. In Visualization, choose Graph

6. Click Save Dashboard, name it Website Metrics
- Add Panels for Metrics
1. Repeat the process to create more panels:

2. Number of Visitors:
```
sum(increase(http_requests_total[5m]))
```
 Shows the number of visitors in the last 5 minutes.

3. Error Count: 
```
sum(increase(http_requests_total{status="500"}[5m]))
```
 Counts 500 errors in the last 5 minutes.

# 📌 Step 4: Add CPU & Memory Monitoring
## 1️⃣ Add Node Exporter to docker-compose.yml
```
 node_exporter:
    image: prom/node-exporter
    ports:
      - "9100:9100"
    networks:
      - monitoring
```
## 2️⃣ Update prometheus.yml
```
 - job_name: "node"
    static_configs:
      - targets: ["node_exporter:9100"]
```
## 3️⃣ Restart Services
```
docker-compose up -d prometheus node_exporter
```
## 4️⃣ Add CPU & Memory Panels in Grafana
- CPU Usage Query:
```
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```
- Memory Usage Query:
```
1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)
```
# 📌 Step 5: Set Up Logging with ELK
## 1️⃣ Add ELK to docker-compose.yml
```
 elasticsearch:
    image: elasticsearch:7.17.0
    ports:
      - "9200:9200"
    networks:
      - monitoring

  logstash:
    image: logstash:7.17.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    networks:
      - monitoring
    depends_on:
      - elasticsearch

  kibana:
    image: kibana:7.17.0
    ports:
      - "5601:5601"
    networks:
      - monitoring
    depends_on:
      - elasticsearch
```
## 2️⃣ Create logstash.conf
```
input {
  file {
    path => "/app/app.log"
    start_position => "beginning"
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "flask-logs"
  }
}
```
## 3️⃣ Run Services
```
docker-compose up -d
```
# 📌 Step 6: Set Up Alerts in Prometheus
## 1️⃣ Create alerts.yml
```
groups:
  - name: flask_alerts
    rules:
      - alert: HighErrorRate
        expr: increase(http_server_requests_total{status="500"}[1m]) > 5
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected!"
```
## 2️⃣ Restart Prometheus
```
docker-compose restart prometheus
```
# 📌 Step 7: Set Up Slack or Email Alerts
## 1️⃣ Add AlertManager to docker-compose.yml
```
 alertmanager:
    image: prom/alertmanager
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    ports:
      - "9093:9093"
    networks:
      - monitoring
```
## 2️⃣ Create alertmanager.yml for Slack
```
receivers:
  - name: 'slack-notifications'
    slack_configs:
      - channel: "#alerts"
        api_url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
```
## 3️⃣ Restart Services
```
docker-compose up -d alertmanager
```
# 📌 Final Step: Submit & Impress Your Instructor 🚀
✅ Docker Compose file

✅ Screenshots of Grafana, Prometheus, Kibana

✅ Short write-up on what you learned

✅ Extra Credit (Slack Alerts, CPU Monitoring, Log Filters)

🎉 Congratulations! You’ve built a complete monitoring system! 🚀💯
