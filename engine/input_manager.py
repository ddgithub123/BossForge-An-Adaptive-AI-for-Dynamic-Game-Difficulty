# engine/input_manager.py
import yaml
from pynput import keyboard

class InputCounter:
    """
    Counts player attack inputs during a M.U.G.E.N. fight.
    Reads key bindings from config/settings.yaml.
    """
    def __init__(self, config_path="config/settings.yaml"):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            self.attack_keys = set(str(k).lower() for k in cfg["keys"]["attack"])
            self.direction_keys = set(str(k).lower() for k in cfg["keys"].get("direction", []))
        except Exception:
            # fallback defaults
            self.attack_keys = set(["1", "2", "3", "4", "5", "6"])
            self.direction_keys = set(["up", "down", "left", "right"])

        self.count = 0
        self._listener = None

    def _on_press(self, key):
        # Try to capture normal keys (1–6)
        try:
            c = key.char.lower()
        except AttributeError:
            # Handle special arrow keys
            if key == keyboard.Key.up:
                c = "up"
            elif key == keyboard.Key.down:
                c = "down"
            elif key == keyboard.Key.left:
                c = "left"
            elif key == keyboard.Key.right:
                c = "right"
            else:
                return

        # Count only attack keys, ignore movement
        if c in self.attack_keys:
            self.count += 1

    def start(self):
        self.count = 0
        self._listener = keyboard.Listener(on_press=self._on_press)
        self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener.join(timeout=0.1)
