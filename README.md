# A Hybrid ML and LLM Pipeline for Log-Based Incident Detection and Remediation

**Bachelor Thesis Project / Project III: Tools for Program Development**  
* **Student:** Cătălinoiu Luis-Roberto (CTI English)  
* **Coordinator:** Ș.l. dr. ing. Ionuț Murarețu  
* **Institution:** National University of Science and Technology Politehnica Bucharest  

---

## 1. System Overview

This project implements an intelligent, hybrid observability and remediation pipeline for modern server-side applications. The platform compresses high-volume unstructured logs into deterministic semantic templates, continuously monitors event frequencies for anomalies using Machine Learning, and triggers automated root-cause analysis and code fixes via Large Language Models (LLMs) and Git.

```
+------------------+
| Server / MockApp |  (Emits streaming logs & simulated faults)
+--------+---------+
         |
         v
+------------------+
|  Drain3 Service  |  (FastAPI - Online log template mining & parameter masking)
+--------+---------+
         |
         +----------------------------+
         |                            |
         v (Enriched Logs)            v (Template Count Metrics)
+------------------+         +------------------+
|   Grafana Loki   |         |    Prometheus    |
+--------+---------+         +--------+---------+
         |                            |
         +-------------+--------------+
                       |
                       v
            +--------------------+
            |      Grafana       |  (Unified Visual Dashboards)
            +--------------------+
                       |
                       v
            +--------------------+
            | ML Anomaly Engine  |  (Isolation Forest / Sequence Deviations)
            +---------+----------+
                      | (Trigger upon anomaly)
                      v
            +--------------------+
            | LLM SRE Remediation|  (Root-cause diagnosis & Git Pull Request)
            +--------------------+
```

---

## 2. Directory Structure

```
.
├── docker-compose.yml              # Multi-container orchestration definition
├── README.md                       # Project documentation
├── .gitignore                      # Git ignore file
├── config/
│   ├── loki-config.yaml            # Loki storage & indexing configuration
│   ├── promtail-config.yaml        # Promtail log shipping configuration
│   ├── prometheus.yml              # Prometheus scrape targets configuration
│   └── grafana/
│       └── provisioning/
│           └── datasources/
│               └── datasources.yaml # Pre-provisioned Loki & Prometheus datasources
├── drain3_service/
│   ├── Dockerfile                  # Python container specification
│   ├── requirements.txt            # Python dependencies (Drain3, FastAPI, Prometheus)
│   ├── drain3.ini                  # Drain3 tree depth and similarity thresholds
│   └── main.py                     # FastAPI template miner & Prometheus exporter
└── mock_app/
    ├── Dockerfile                  # Mock app container specification
    ├── requirements.txt            # Dependencies
    └── app.py                      # Realistic server traffic & error burst generator
```

---

## 3. Quickstart Guide (Using Docker Compose)

### 3.1 Start all services
Ensure Docker Desktop is running on your machine, then execute:

```bash
docker compose up --build -d
```

### 3.2 Access Service Dashboards & Endpoints
| Component | URL | Credentials / Notes |
| :--- | :--- | :--- |
| **Grafana** | `http://localhost:3000` | User: `admin` \| Pass: `admin` |
| **Prometheus** | `http://localhost:9090` | Targets: `http://localhost:9090/targets` |
| **Drain3 API Docs** | `http://localhost:8000/docs` | Interactive Swagger API UI |
| **Drain3 Templates** | `http://localhost:8000/templates` | Active discovered log templates |
| **Drain3 Metrics** | `http://localhost:8000/metrics` | Prometheus raw metric output |
| **Loki Readiness** | `http://localhost:3100/ready` | Returns `ready` when operational |

### 3.3 Stop the stack
```bash
docker compose down
```

---

## 4. Standalone Testing (Without Docker)

You can also run and test the Python services locally on your machine:

1. **Start the Drain3 Service:**
   ```bash
   cd drain3_service
   pip install -r requirements.txt
   python main.py
   ```
2. **Start the Mock Server:**
   ```bash
   cd mock_app
   python app.py
   ```
3. Visit `http://localhost:8000/templates` in your browser to see discovered templates in real-time!
