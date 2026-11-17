import os
import time
import json
import logging
from typing import List, Optional
import requests
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Drain3Service")

# Configuration
LOKI_URL = os.getenv("LOKI_URL", "http://loki:3100/loki/api/v1/push")
FORWARD_TO_LOKI = os.getenv("FORWARD_TO_LOKI", "true").lower() == "true"

# Initialize Drain3 Template Miner
config = TemplateMinerConfig()
config_file = os.path.join(os.path.dirname(__file__), "drain3.ini")
if os.path.exists(config_file):
    config.load(config_file)
    logger.info(f"Loaded Drain3 config from {config_file}")
else:
    config.drain_depth = 4
    config.drain_sim_th = 0.5

template_miner = TemplateMiner(config=config)
logger.info("Drain3 TemplateMiner successfully initialized.")

# Prometheus Metrics
LOGS_PROCESSED_TOTAL = Counter(
    "drain3_processed_logs_total",
    "Total raw log lines processed by Drain3"
)
TEMPLATE_OCCURRENCES_TOTAL = Counter(
    "drain3_template_occurrences_total",
    "Count of occurrences for each Drain3 template",
    ["cluster_id", "template_str"]
)
TOTAL_CLUSTERS_GAUGE = Gauge(
    "drain3_clusters_total",
    "Total number of unique log clusters/templates identified"
)
ERROR_LOGS_TOTAL = Counter(
    "drain3_error_logs_total",
    "Total error/critical logs processed",
    ["level"]
)

app = FastAPI(
    title="Drain3 Log Template Mining & Prometheus Metrics Service",
    description="Processes streaming server logs, extracts templates via Drain3, and publishes Prometheus metrics.",
    version="1.0.0"
)

class LogBatchRequest(BaseModel):
    service: Optional[str] = "server-backend"
    logs: List[str]

class SingleLogRequest(BaseModel):
    service: Optional[str] = "server-backend"
    log: str

def push_to_loki(service: str, cluster_id: int, template_str: str, raw_line: str):
    """Optionally forwards enriched logs directly to Loki."""
    if not FORWARD_TO_LOKI:
        return
    try:
        now_ns = str(time.time_ns())
        payload = {
            "streams": [
                {
                    "stream": {
                        "job": "drain3-enriched",
                        "service": service,
                        "cluster_id": str(cluster_id),
                        "has_error": "true" if any(k in raw_line.upper() for k in ["ERROR", "CRITICAL", "EXCEPTION", "FAIL"]) else "false"
                    },
                    "values": [
                        [now_ns, f"[Template ID: {cluster_id}] {raw_line}"]
                    ]
                }
            ]
        }
        requests.post(LOKI_URL, json=payload, timeout=2.0)
    except Exception as e:
        logger.debug(f"Could not forward to Loki: {e}")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "total_templates_discovered": len(template_miner.drain.id_to_cluster),
        "total_logs_processed": LOGS_PROCESSED_TOTAL._value.get()
    }

@app.post("/ingest")
def ingest_single_log(payload: SingleLogRequest, background_tasks: BackgroundTasks):
    line = payload.log.strip()
    if not line:
        return {"status": "skipped", "reason": "empty line"}

    LOGS_PROCESSED_TOTAL.inc()

    # Track error level
    line_upper = line.upper()
    if "ERROR" in line_upper:
        ERROR_LOGS_TOTAL.labels(level="ERROR").inc()
    elif "CRITICAL" in line_upper or "FATAL" in line_upper:
        ERROR_LOGS_TOTAL.labels(level="CRITICAL").inc()
    elif "WARN" in line_upper:
        ERROR_LOGS_TOTAL.labels(level="WARNING").inc()

    # Process through Drain3
    result = template_miner.add_log_message(line)
    cluster_id = result["cluster_id"]
    template_str = result["template_mined"]
    change_type = result["change_type"]

    # Update Prometheus
    # Truncate template_str for metric label safety if too long
    safe_template_label = (template_str[:90] + "...") if len(template_str) > 90 else template_str
    TEMPLATE_OCCURRENCES_TOTAL.labels(
        cluster_id=str(cluster_id),
        template_str=safe_template_label
    ).inc()
    TOTAL_CLUSTERS_GAUGE.set(len(template_miner.drain.id_to_cluster))

    # Async forward to Loki
    background_tasks.add_task(push_to_loki, payload.service, cluster_id, template_str, line)

    return {
        "cluster_id": cluster_id,
        "template": template_str,
        "change_type": change_type
    }

@app.post("/ingest-batch")
def ingest_log_batch(payload: LogBatchRequest, background_tasks: BackgroundTasks):
    results = []
    for line in payload.logs:
        line_clean = line.strip()
        if not line_clean:
            continue
        LOGS_PROCESSED_TOTAL.inc()
        res = template_miner.add_log_message(line_clean)
        cluster_id = res["cluster_id"]
        template_str = res["template_mined"]
        safe_label = (template_str[:90] + "...") if len(template_str) > 90 else template_str
        TEMPLATE_OCCURRENCES_TOTAL.labels(
            cluster_id=str(cluster_id),
            template_str=safe_label
        ).inc()
        results.append({
            "cluster_id": cluster_id,
            "template": template_str
        })
    TOTAL_CLUSTERS_GAUGE.set(len(template_miner.drain.id_to_cluster))
    return {
        "processed_count": len(results),
        "total_active_clusters": len(template_miner.drain.id_to_cluster)
    }

@app.get("/templates")
def get_all_templates():
    clusters = []
    for cid, cluster in template_miner.drain.id_to_cluster.items():
        clusters.append({
            "cluster_id": cid,
            "template": cluster.get_template(),
            "size": cluster.size
        })
    # Sort descending by size/occurrences
    clusters.sort(key=lambda x: x["size"], reverse=True)
    return {
        "total_unique_templates": len(clusters),
        "clusters": clusters
    }

@app.get("/metrics")
def get_prometheus_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
