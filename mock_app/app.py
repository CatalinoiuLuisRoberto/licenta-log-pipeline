import os
import time
import random
import uuid
import datetime
import requests
import logging

LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "/var/log/app/server.log")
DRAIN3_INGEST_URL = os.getenv("DRAIN3_INGEST_URL", "http://drain3-service:8000/ingest")
SEND_TO_DRAIN3_HTTP = os.getenv("SEND_TO_DRAIN3_HTTP", "true").lower() == "true"
LOGS_PER_SECOND = float(os.getenv("LOGS_PER_SECOND", "5.0"))

# Ensure directory exists
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

# Logger setup
file_handler = logging.FileHandler(LOG_FILE_PATH)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger = logging.getLogger("MockServer")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

USERS = [f"user_{i}" for i in range(101, 150)]
ENDPOINTS = [
    ("/api/v1/auth/login", "POST", 200),
    ("/api/v1/auth/refresh", "POST", 200),
    ("/api/v1/products", "GET", 200),
    ("/api/v1/products/search", "GET", 200),
    ("/api/v1/cart/items", "POST", 201),
    ("/api/v1/orders/checkout", "POST", 200),
    ("/api/v1/user/profile", "GET", 200),
    ("/healthz", "GET", 200),
]

IPS = [f"192.168.1.{i}" for i in range(10, 80)] + [f"10.0.0.{i}" for i in range(100, 220)]

def generate_normal_log():
    endpoint, method, status = random.choice(ENDPOINTS)
    user = random.choice(USERS)
    client_ip = random.choice(IPS)
    latency = random.randint(12, 180)
    ts = datetime.datetime.now().isoformat()

    actions = [
        f"{ts} [INFO] [HTTP] {method} {endpoint} - client={client_ip} status={status} duration={latency}ms",
        f"{ts} [INFO] [AuthService] User {user} successfully authenticated from {client_ip} with session {uuid.uuid4().hex[:8]}",
        f"{ts} [INFO] [OrderService] Created order #{random.randint(5000, 9999)} for {user} containing {random.randint(1, 5)} items",
        f"{ts} [DEBUG] [DatabasePool] Executed query SELECT * FROM inventory WHERE product_id={random.randint(1, 1000)} in {random.randint(2, 25)}ms",
        f"{ts} [INFO] [CacheManager] Cache hit for key 'product_catalog_page_{random.randint(1, 10)}' (TTL 300s)",
    ]
    return random.choice(actions)

def generate_error_log():
    user = random.choice(USERS)
    client_ip = random.choice(IPS)
    ts = datetime.datetime.now().isoformat()

    errors = [
        f"{ts} [ERROR] [DatabasePool] ConnectionPoolTimeoutException: pool size 50 exhausted after 30000ms waiting for available connection",
        f"{ts} [ERROR] [PaymentGateway] NullPointerException: token was null for order #{random.randint(5000, 9999)} at PaymentController.py:84",
        f"{ts} [CRITICAL] [SystemHealth] HeapMemoryExceededException: 94.8% memory usage on node-03, triggering garbage collection",
        f"{ts} [ERROR] [AuthService] Failed login attempt for user {user} from IP {client_ip} (invalid password hash, attempt 4)",
        f"{ts} [WARNING] [RateLimiter] IP {client_ip} exceeded threshold: 120 requests/minute, rate-limiting applied",
        f"{ts} [ERROR] [OrderService] Order #{random.randint(5000, 9999)} failed rollback transaction: deadlock detected on table 'orders'"
    ]
    return random.choice(errors)

def emit_log(line: str):
    logger.info(line)
    if SEND_TO_DRAIN3_HTTP:
        try:
            requests.post(DRAIN3_INGEST_URL, json={"service": "mock-app", "log": line}, timeout=0.5)
        except Exception:
            pass

def run():
    print(f"🚀 Mock Server started. Writing to {LOG_FILE_PATH} and streaming to {DRAIN3_INGEST_URL}...")
    interval = 1.0 / max(LOGS_PER_SECOND, 0.1)

    step = 0
    while True:
        step += 1
        # 10% chance of an error or sudden error burst
        if random.random() < 0.12:
            burst_size = random.randint(1, 4)
            for _ in range(burst_size):
                emit_log(generate_error_log())
        else:
            emit_log(generate_normal_log())

        time.sleep(interval)

if __name__ == "__main__":
    run()
