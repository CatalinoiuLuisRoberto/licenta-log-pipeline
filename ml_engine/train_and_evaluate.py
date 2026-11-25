import os
import time
import joblib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve, precision_recall_fscore_support

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT_DIR, exist_ok=True)

np.random.seed(42)

def generate_synthetic_log_dataset(n_samples=2000, n_templates=13, anomaly_ratio=0.08):
    """
    Simulates sliding-window feature vectors representing occurrences of 13 Drain3 templates
    over 60-second intervals.
    
    Normal templates (0-3: Login, Browse, Cart, DB query): high counts with Poisson distribution.
    Rare/Error templates (4: NullPointer, 11: DB Timeout, 12: Memory): ~0 in normal, high in anomalies.
    """
    n_anomalies = int(n_samples * anomaly_ratio)
    n_normal = n_samples - n_anomalies
    
    # 1. Normal traffic features
    X_normal = np.zeros((n_normal, n_templates))
    # Normal operations: high activity
    X_normal[:, 0] = np.random.poisson(lam=45, size=n_normal)   # Login
    X_normal[:, 1] = np.random.poisson(lam=80, size=n_normal)   # Product browse
    X_normal[:, 2] = np.random.poisson(lam=25, size=n_normal)   # Add to cart
    X_normal[:, 3] = np.random.poisson(lam=110, size=n_normal)  # Fast DB select
    X_normal[:, 4] = np.random.poisson(lam=15, size=n_normal)   # Order checkout
    X_normal[:, 5:9] = np.random.poisson(lam=10, size=(n_normal, 4)) # Cache hits, info logs
    # Normal background noise for errors (very close to 0)
    X_normal[:, 9:] = np.random.binomial(n=1, p=0.01, size=(n_normal, 4))
    
    y_normal = np.ones(n_normal) # 1 = Normal in sklearn outlier detection
    
    # 2. Anomalous traffic features (outages, memory leaks, payment crashes)
    X_anomaly = np.zeros((n_anomalies, n_templates))
    for i in range(n_anomalies):
        scenario = np.random.choice(["payment_crash", "db_timeout", "ddos_auth", "memory_exhaustion"])
        if scenario == "payment_crash":
            # Normal drops slightly, NullPointer crashes explode
            X_anomaly[i, 0] = np.random.poisson(lam=30)
            X_anomaly[i, 1] = np.random.poisson(lam=40)
            X_anomaly[i, 9] = np.random.poisson(lam=25) # NullPointerException burst!
        elif scenario == "db_timeout":
            X_anomaly[i, 3] = np.random.poisson(lam=10) # regular DB queries stall
            X_anomaly[i, 10] = np.random.poisson(lam=35) # DB ConnectionPoolTimeout burst!
        elif scenario == "ddos_auth":
            X_anomaly[i, 0] = np.random.poisson(lam=250) # massive auth surge
            X_anomaly[i, 11] = np.random.poisson(lam=45) # RateLimiter applied
        else: # memory_exhaustion
            X_anomaly[i, 12] = np.random.poisson(lam=18) # HeapMemoryExceeded
            X_anomaly[i, :4] = np.random.poisson(lam=5)   # system throughput stalls
            
    y_anomaly = -np.ones(n_anomalies) # -1 = Anomaly in sklearn
    
    X = np.vstack([X_normal, X_anomaly])
    y = np.concatenate([y_normal, y_anomaly])
    
    # Shuffle
    indices = np.random.permutation(n_samples)
    return X[indices], y[indices]

def train_and_evaluate():
    print("==================================================")
    print("Machine Learning Pipeline: Training Anomaly Detection Models")
    print("==================================================")
    
    X, y = generate_synthetic_log_dataset(n_samples=2500, anomaly_ratio=0.08)
    
    # Split train (normal only for unsupervised training) and test (mixed)
    # In unsupervised outlier detection, we train primarily on normal data
    normal_mask = (y == 1)
    X_train = X[normal_mask][:1600]
    
    # Test set with both normal and anomalies
    X_test = X[1600:]
    y_test = y[1600:]
    
    # Convert y_test to binary (0 = Normal, 1 = Anomaly) for standard metrics
    y_true_binary = np.where(y_test == -1, 1, 0)
    
    # 1. Model A: Isolation Forest
    print("\n1. Training Isolation Forest Model...")
    t0 = time.time()
    iso_forest = IsolationForest(
        n_estimators=150,
        contamination=0.08,
        max_samples='auto',
        random_state=42,
        n_jobs=-1
    )
    iso_forest.fit(X_train)
    iso_train_time = time.time() - t0
    
    # Predictions (-1 = Anomaly, 1 = Normal)
    iso_preds = iso_forest.predict(X_test)
    iso_preds_binary = np.where(iso_preds == -1, 1, 0)
    iso_scores = -iso_forest.score_samples(X_test) # Higher score = more anomalous
    
    # Isolation Forest Metrics
    prec, rec, f1, _ = precision_recall_fscore_support(y_true_binary, iso_preds_binary, average='binary')
    iso_auc = roc_auc_score(y_true_binary, iso_scores)
    cm_iso = confusion_matrix(y_true_binary, iso_preds_binary)
    
    print(f"Isolation Forest Results (Train time: {iso_train_time:.3f}s):")
    print(f"  Precision: {prec*100:.2f}%")
    print(f"  Recall:    {rec*100:.2f}%")
    print(f"  F1-Score:  {f1*100:.2f}%")
    print(f"  ROC-AUC:   {iso_auc:.4f}")
    
    # 2. Model B: One-Class SVM (Baseline comparison)
    print("\n2. Training One-Class SVM Baseline...")
    t0 = time.time()
    oc_svm = OneClassSVM(kernel='rbf', gamma='scale', nu=0.08)
    oc_svm.fit(X_train)
    svm_train_time = time.time() - t0
    
    svm_preds = oc_svm.predict(X_test)
    svm_preds_binary = np.where(svm_preds == -1, 1, 0)
    svm_scores = -oc_svm.score_samples(X_test)
    
    prec_svm, rec_svm, f1_svm, _ = precision_recall_fscore_support(y_true_binary, svm_preds_binary, average='binary')
    svm_auc = roc_auc_score(y_true_binary, svm_scores)
    cm_svm = confusion_matrix(y_true_binary, svm_preds_binary)
    
    print(f"One-Class SVM Results (Train time: {svm_train_time:.3f}s):")
    print(f"  Precision: {prec_svm*100:.2f}%")
    print(f"  Recall:    {rec_svm*100:.2f}%")
    print(f"  F1-Score:  {f1_svm*100:.2f}%")
    print(f"  ROC-AUC:   {svm_auc:.4f}")
    
    # Save Model
    model_save_path = os.path.join(OUT_DIR, "isolation_forest_model.joblib")
    joblib.dump(iso_forest, model_save_path)
    print(f"\nSaved trained model to: {model_save_path}")
    
    # Generate Publication-Quality Evaluation Plot
    generate_evaluation_plot(y_true_binary, iso_scores, iso_preds_binary, cm_iso, svm_scores, cm_svm)
    
    return {
        "iso_metrics": (prec, rec, f1, iso_auc),
        "svm_metrics": (prec_svm, rec_svm, f1_svm, svm_auc),
        "cm_iso": cm_iso
    }

def generate_evaluation_plot(y_true, iso_scores, iso_preds, cm_iso, svm_scores, cm_svm):
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), dpi=300)
    
    # Plot 1: Confusion Matrix for Isolation Forest
    ax1 = axes[0]
    im1 = ax1.imshow(cm_iso, interpolation='nearest', cmap=plt.cm.Blues)
    ax1.set_title("Confusion Matrix (Isolation Forest)", fontsize=12, fontweight='bold', pad=10)
    fig.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
    tick_marks = np.arange(2)
    ax1.set_xticks(tick_marks)
    ax1.set_xticklabels(['Normal (0)', 'Anomaly (1)'])
    ax1.set_yticks(tick_marks)
    ax1.set_yticklabels(['Normal (0)', 'Anomaly (1)'])
    ax1.set_ylabel('True Label', fontweight='bold')
    ax1.set_xlabel('Predicted Label', fontweight='bold')
    
    thresh = cm_iso.max() / 2.
    for i in range(cm_iso.shape[0]):
        for j in range(cm_iso.shape[1]):
            ax1.text(j, i, format(cm_iso[i, j], 'd'),
                     ha="center", va="center",
                     color="white" if cm_iso[i, j] > thresh else "black",
                     fontsize=14, fontweight='bold')
                     
    # Plot 2: ROC Curves Comparison
    ax2 = axes[1]
    fpr_iso, tpr_iso, _ = roc_curve(y_true, iso_scores)
    auc_iso = roc_auc_score(y_true, iso_scores)
    
    fpr_svm, tpr_svm, _ = roc_curve(y_true, svm_scores)
    auc_svm = roc_auc_score(y_true, svm_scores)
    
    ax2.plot(fpr_iso, tpr_iso, color='#1F4E79', lw=2.5, label=f'Isolation Forest (AUC = {auc_iso:.3f})')
    ax2.plot(fpr_svm, tpr_svm, color='#C00000', lw=2.0, linestyle='--', label=f'One-Class SVM (AUC = {auc_svm:.3f})')
    ax2.plot([0, 1], [0, 1], color='gray', linestyle=':', lw=1.5, label='Random Chance')
    ax2.set_xlim([0.0, 1.0])
    ax2.set_ylim([0.0, 1.05])
    ax2.set_xlabel('False Positive Rate (1 - Specificity)', fontweight='bold')
    ax2.set_ylabel('True Positive Rate (Sensitivity / Recall)', fontweight='bold')
    ax2.set_title('Receiver Operating Characteristic (ROC)', fontsize=12, fontweight='bold', pad=10)
    ax2.legend(loc="lower right")
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Anomaly Score Distribution
    ax3 = axes[2]
    normal_scores = iso_scores[y_true == 0]
    anomaly_scores = iso_scores[y_true == 1]
    
    ax3.hist(normal_scores, bins=35, alpha=0.65, color='#2E75B6', label='Normal Logs', density=True)
    ax3.hist(anomaly_scores, bins=35, alpha=0.75, color='#C00000', label='Injected Outages', density=True)
    ax3.axvline(x=np.percentile(normal_scores, 92), color='black', linestyle='--', lw=2, label='Decision Boundary')
    ax3.set_xlabel('Anomaly Score (Higher = Outlier)', fontweight='bold')
    ax3.set_ylabel('Density', fontweight='bold')
    ax3.set_title('Anomaly Score Separation', fontsize=12, fontweight='bold', pad=10)
    ax3.legend(loc="upper right")
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = os.path.join(OUT_DIR, "evaluation_metrics.png")
    plt.savefig(plot_path, bbox_inches='tight')
    plt.close()
    print(f"Saved evaluation plots to: {plot_path}")

if __name__ == '__main__':
    train_and_evaluate()
