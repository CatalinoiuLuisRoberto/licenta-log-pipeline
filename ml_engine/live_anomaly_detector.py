import os
import time
import requests
import joblib
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "isolation_forest_model.joblib")
TEMPLATES_URL = os.getenv("TEMPLATES_URL", "http://localhost:8000/templates")

def run_live_detector():
    print("==================================================")
    print("Live SRE Anomaly Detector: Isolation Forest Inference")
    print("==================================================")
    
    if not os.path.exists(MODEL_PATH):
        print("Model not found! Running train_and_evaluate.py first...")
        from train_and_evaluate import train_and_evaluate
        train_and_evaluate()
        
    model = joblib.load(MODEL_PATH)
    print("Loaded trained Isolation Forest model.")
    print(f"Polling Drain3 templates from {TEMPLATES_URL} every 4 seconds...\n")
    
    # Track historical counts to measure delta (per minute rate)
    last_sizes = {}
    
    while True:
        try:
            res = requests.get(TEMPLATES_URL, timeout=3.0)
            if res.status_code == 200:
                data = res.json()
                clusters = data.get("clusters", [])
                
                # Construct 13-dimensional feature vector based on cluster sizes
                feature_vector = np.zeros(13)
                critical_error_flag = False
                trigger_template = None
                
                for c in clusters:
                    cid = c.get("cluster_id", 0)
                    size = c.get("size", 0)
                    tpl = c.get("template", "")
                    
                    # Delta since last poll
                    delta = size - last_sizes.get(cid, 0)
                    last_sizes[cid] = size
                    
                    if 1 <= cid <= 13:
                        feature_vector[cid - 1] = delta
                        
                    # Check for explicit critical exceptions
                    if any(k in tpl.upper() for k in ["NULLPOINTER", "TIMEOUT", "DEADLOCK", "HEAPMEMORY"]):
                        if delta > 0:
                            critical_error_flag = True
                            trigger_template = tpl
                            
                # Predict with model (-1 = Anomaly, 1 = Normal)
                # Reshape for single sample prediction
                pred = model.predict(feature_vector.reshape(1, -1))[0]
                anomaly_score = -model.score_samples(feature_vector.reshape(1, -1))[0]
                
                status_str = "🚨 ANOMALY DETECTED" if (pred == -1 or critical_error_flag) else "✅ SYSTEM NORMAL"
                print(f"[{time.strftime('%H:%M:%S')}] Status: {status_str} | Anomaly Score: {anomaly_score:.3f} | Active Delta: {int(np.sum(feature_vector))}")
                
                if pred == -1 or critical_error_flag:
                    print(f"  └── ⚠️ High risk event surge! Triggering SRE alert.")
                    if trigger_template:
                        print(f"  └── 🔍 Root Cause Template: {trigger_template}")
                    print(f"  └── 🤖 Handing off to LLM Engine for Git Source Code Patching...\n")
            else:
                print(f"Drain3 service returned status {res.status_code}")
        except Exception as e:
            print(f"Waiting for Drain3 service to be reachable ({e})...")
            
        time.sleep(4.0)

if __name__ == '__main__':
    run_live_detector()
