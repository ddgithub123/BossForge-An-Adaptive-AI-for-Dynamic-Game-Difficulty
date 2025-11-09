# ================================================
# BossForge Adaptive AI Optimization Simulation
# ================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- 1️⃣ LOAD DATASET ---
df = pd.read_csv("bossforge_telemetry.csv")  # your given CSV
X = df[["aggression", "reaction_time", "attack_rate"]].values
y = df["win"].values.reshape(-1, 1)

# Normalize features for stable training
X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)

# --- 2️⃣ DEFINE MODEL ---
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def loss_fn(y_true, y_pred):
    return np.mean((y_true - y_pred) ** 2)

# Initialize weights and bias
np.random.seed(42)
weights = np.random.randn(X.shape[1], 1)
bias = 0.0


# --- 3️⃣ GRADIENT DESCENT FUNCTION ---
def gradient_descent(X, y, lr=0.01, epochs=300):
    w, b = np.copy(weights), bias
    losses = []
    for i in range(epochs):
        y_pred = sigmoid(np.dot(X, w) + b)
        error = y_pred - y
        dw = np.dot(X.T, error) / len(X)
        db = np.mean(error)
        w -= lr * dw
        b -= lr * db
        losses.append(loss_fn(y, y_pred))
    return w, b, losses


# --- 4️⃣ ADAGRAD FUNCTION ---
def adagrad(X, y, lr=0.1, epochs=300, epsilon=1e-8):
    w, b = np.copy(weights), bias
    Gw = np.zeros_like(w)
    Gb = 0
    losses = []
    for i in range(epochs):
        y_pred = sigmoid(np.dot(X, w) + b)
        error = y_pred - y
        dw = np.dot(X.T, error) / len(X)
        db = np.mean(error)

        # Update with accumulated squared gradients
        Gw += dw**2
        Gb += db**2
        w -= (lr / (np.sqrt(Gw) + epsilon)) * dw
        b -= (lr / (np.sqrt(Gb) + epsilon)) * db
        losses.append(loss_fn(y, y_pred))
    return w, b, losses


# --- 5️⃣ ADAM OPTIMIZER FUNCTION ---
def adam(X, y, lr=0.01, epochs=300, beta1=0.9, beta2=0.999, epsilon=1e-8):
    w, b = np.copy(weights), bias
    mw, vw = np.zeros_like(w), np.zeros_like(w)
    mb, vb = 0, 0
    losses = []

    for t in range(1, epochs + 1):
        y_pred = sigmoid(np.dot(X, w) + b)
        error = y_pred - y
        dw = np.dot(X.T, error) / len(X)
        db = np.mean(error)

        # Momentum updates
        mw = beta1 * mw + (1 - beta1) * dw
        vw = beta2 * vw + (1 - beta2) * (dw**2)
        mb = beta1 * mb + (1 - beta1) * db
        vb = beta2 * vb + (1 - beta2) * (db**2)

        # Bias correction
        mw_corr = mw / (1 - beta1**t)
        vw_corr = vw / (1 - beta2**t)
        mb_corr = mb / (1 - beta1**t)
        vb_corr = vb / (1 - beta2**t)

        # Parameter updates
        w -= lr * mw_corr / (np.sqrt(vw_corr) + epsilon)
        b -= lr * mb_corr / (np.sqrt(vb_corr) + epsilon)

        losses.append(loss_fn(y, y_pred))
    return w, b, losses


# --- 6️⃣ RUN OPTIMIZERS ---
gd_w, gd_b, gd_loss = gradient_descent(X, y)
adagrad_w, adagrad_b, adagrad_loss = adagrad(X, y)
adam_w, adam_b, adam_loss = adam(X, y)

# --- 7️⃣ VISUALIZE TRAINING PERFORMANCE ---
plt.figure(figsize=(8,5))
plt.plot(gd_loss, label="Gradient Descent", color="tomato")
plt.plot(adagrad_loss, label="Adagrad", color="royalblue")
plt.plot(adam_loss, label="Adam", color="green")
plt.title("Optimization Loss Convergence for Adaptive AI")
plt.xlabel("Epochs")
plt.ylabel("MSE Loss")
plt.legend()
plt.grid(alpha=0.4)
plt.tight_layout()
plt.show()

# --- 8️⃣ FINAL METRICS ---
print("Final Loss (Gradient Descent):", gd_loss[-1])
print("Final Loss (Adagrad):", adagrad_loss[-1])
print("Final Loss (Adam):", adam_loss[-1])
