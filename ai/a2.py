import matplotlib.pyplot as plt
import numpy as np

# --- 1️⃣ WIN RATE COMPARISON (same as before) ---
before_adapt_win_rate = 0.15
after_adapt_win_rate = 0.45

plt.figure(figsize=(6,5))
plt.bar(["Before Adaptation", "After Adaptation"],
        [before_adapt_win_rate, after_adapt_win_rate],
        color=["lightcoral", "mediumseagreen"])
plt.title("Player Win Rate Before vs After Adaptation", fontsize=14, weight='bold')
plt.ylabel("Win Rate", fontsize=12)
plt.ylim(0, 1)
plt.grid(axis='y', alpha=0.5)
plt.tight_layout()
plt.show()


# --- 2️⃣ REACTION TIME TREND (Inverse and Generalized) ---
sessions = np.arange(1, 51)

# Simulate realistic adaptive oscillations (reaction time sometimes increases slightly)
reaction_time = 0.3 + 0.1 * np.sin(sessions/3) + np.random.normal(0, 0.02, 50)
reaction_time = np.clip(reaction_time, 0.25, 0.45)  # keep values in logical range

plt.figure(figsize=(8,5))
plt.plot(sessions, reaction_time, color="darkorange", marker="o", markersize=4, linewidth=2)
plt.title("Adaptive Reaction Time Variation Over Sessions", fontsize=14, weight='bold')
plt.xlabel("Session Number", fontsize=12)
plt.ylabel("Reaction Time (seconds)", fontsize=12)
plt.grid(alpha=0.4)
plt.tight_layout()
plt.show()
