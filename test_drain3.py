from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig

config = TemplateMinerConfig()
config.drain_depth = 4
config.drain_sim_th = 0.5
miner = TemplateMiner(config=config)

sample_logs = [
    "2026-11-18T00:20:10 [INFO] [HTTP] GET /api/v1/products - client=192.168.1.15 status=200 duration=45ms",
    "2026-11-18T00:20:11 [INFO] [HTTP] GET /api/v1/products - client=192.168.1.88 status=200 duration=120ms",
    "2026-11-18T00:20:12 [INFO] [AuthService] User user_101 successfully authenticated with session abc12345",
    "2026-11-18T00:20:13 [INFO] [AuthService] User user_142 successfully authenticated with session def67890",
    "2026-11-18T00:20:14 [ERROR] [DatabasePool] ConnectionPoolTimeoutException: pool size 50 exhausted after 30000ms"
]

print("--- DRAIN3 SAMPLE TEST ---")
for log in sample_logs:
    res = miner.add_log_message(log)
    cid = res['cluster_id']
    tpl = res['template_mined']
    print(f"[Cluster {cid}] -> {tpl}")

print(f"\nUnique templates discovered: {len(miner.drain.id_to_cluster)}")
