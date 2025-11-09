# data/fight_data.py
import os, csv, pandas as pd, numpy as np

COLUMNS = ["timestamp","aggression","reaction_time","attack_inputs","attack_rate","fight_time","win"]

def append_row(csv_path, row):
    newfile = not os.path.exists(csv_path)
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if newfile:
            writer.writeheader()
        writer.writerow(row)

def _read_df(csv_path):
    if not os.path.exists(csv_path):
        return None
    df = pd.read_csv(csv_path)
    # ensure columns exist
    for c in COLUMNS:
        if c not in df.columns:
            df[c] = 0
    # coerce types safely
    df["attack_inputs"] = pd.to_numeric(df["attack_inputs"].fillna(0), errors='coerce').fillna(0).astype(int)
    df["attack_rate"] = pd.to_numeric(df["attack_rate"].fillna(0.0), errors='coerce').fillna(0.0).astype(float)
    df["win"] = pd.to_numeric(df["win"].fillna(0), errors='coerce').fillna(0).astype(int)
    return df

def compute_update(csv_path, current_aggr, current_react, cfg):
    df = _read_df(csv_path)
    if df is None or len(df) == 0:
        return current_aggr, current_react, 0.0

    if len(df) < 8:
        win_rate = float(df['win'].mean()) if len(df) > 0 else 0.5
        delta = cfg["LEARNING_RATE"] * (cfg["TARGET_WINRATE"] - win_rate)
        return np.clip(current_aggr + delta, cfg["MIN_AGGR"], cfg["MAX_AGGR"]), \
               np.clip(current_react - delta, cfg["MIN_REACTION"], cfg["MAX_REACTION"]), win_rate

    dfw = df.tail(cfg["WINDOW"])
    # if attack_rate or fight_time are constant/zero, add tiny noise to avoid singular matrices
    X = dfw[["aggression","reaction_time","attack_rate","fight_time"]].astype(float).values
    y = dfw["win"].astype(float).values
    A = np.hstack([np.ones((X.shape[0],1)), X])
    try:
        beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    except Exception as e:
        print("[fight_data] lstsq failed:", e)
        # fallback: small step
        win_rate = float(dfw['win'].mean())
        delta = cfg["LEARNING_RATE"] * (cfg["TARGET_WINRATE"] - win_rate)
        return np.clip(current_aggr + delta, cfg["MIN_AGGR"], cfg["MAX_AGGR"]), \
               np.clip(current_react - delta, cfg["MIN_REACTION"], cfg["MAX_REACTION"]), win_rate

    mean_attack_rate = float(dfw['attack_rate'].mean()) if 'attack_rate' in dfw else 0.0
    mean_fight_time = float(dfw['fight_time'].mean()) if 'fight_time' in dfw else 1.0
    x_curr = np.array([1.0, current_aggr, current_react, mean_attack_rate, mean_fight_time])
    pred = float(x_curr.dot(beta))
    beta_aggr = float(beta[1]) if len(beta) > 1 else 0.0
    beta_react = float(beta[2]) if len(beta) > 2 else 0.0
    denom = beta_aggr**2 + beta_react**2 + 1e-9
    factor = cfg["LEARNING_RATE"] * (cfg["TARGET_WINRATE"] - pred) / denom
    delta_aggr = factor * beta_aggr
    delta_react = factor * beta_react
    new_aggr = np.clip(current_aggr + delta_aggr, cfg["MIN_AGGR"], cfg["MAX_AGGR"])
    new_react = np.clip(current_react + delta_react, cfg["MIN_REACTION"], cfg["MAX_REACTION"])
    return new_aggr, new_react, float(dfw['win'].mean())
