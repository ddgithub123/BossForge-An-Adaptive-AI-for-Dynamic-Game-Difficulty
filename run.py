import json, yaml, time
from core.orchestrator import Orchestrator
#from data.fight_data import compute_update

cfg = yaml.safe_load(open("config/settings.yaml"))
paths = json.load(open("config/paths.json"))

orc = Orchestrator(cfg, paths)
try:
    while True:
        orc.run_one_match()
        print("=== next match will start automatically (Ctrl+C to stop) ===")
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped by user.")
