# ai/adaptive_boss.py
import os, json
import numpy as np
from data.fight_data import _read_df, compute_update as regression_compute

class AdaptiveBoss:
    def __init__(self, cfg, state_path="ai/state.json"):
        self.cfg = cfg
        self.state_path = state_path
        self.state = {"integral": 0.0, "prev_error": 0.0}
        if os.path.exists(self.state_path):
            try:
                self.state.update(json.load(open(self.state_path, "r")))
            except Exception:
                pass

    def _save_state(self):
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        with open(self.state_path, "w") as f:
            json.dump(self.state, f)

    def update(self, csv_path, current_aggr, current_react, compute_fn=None):
        mode = self.cfg.get("ADAPTATION_MODE", "PID").upper()
        if mode == "PID":
            df = _read_df(csv_path)
            if df is None or len(df) == 0:
                winrate = 0.5
            else:
                winrate = float(df.tail(self.cfg.get("WINDOW",20))['win'].mean())
            error = self.cfg.get("TARGET_WINRATE", 0.5) - winrate
            kp = self.cfg.get("PID_KP", 0.5)
            ki = self.cfg.get("PID_KI", 0.05)
            kd = self.cfg.get("PID_KD", 0.01)
            self.state["integral"] += error
            derivative = error - self.state.get("prev_error", 0.0)
            delta = kp*error + ki*self.state["integral"] + kd*derivative
            new_aggr = np.clip(current_aggr + delta, self.cfg.get("MIN_AGGR", 0.0), self.cfg.get("MAX_AGGR", 1.0))
            new_react = np.clip(current_react - delta, self.cfg.get("MIN_REACTION", 0.1), self.cfg.get("MAX_REACTION", 2.5))
            self.state["prev_error"] = error
            self._save_state()
            print(f"[adaptive_boss:PID] winrate={winrate:.3f} error={error:.3f} delta={delta:.4f}")
            return new_aggr, new_react

        # fallback: regression-based compute (existing behavior)
        if compute_fn is None:
            compute_fn = regression_compute
        res = compute_fn(csv_path, current_aggr, current_react, self.cfg)
        # compute_fn returns (new_aggr, new_react, winrate)
        return res[0], res[1]
