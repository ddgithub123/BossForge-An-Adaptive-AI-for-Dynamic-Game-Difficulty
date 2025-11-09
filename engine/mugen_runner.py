import subprocess, time, os

class MugenRunner:
    def __init__(self, exe_path, workdir):
        self.exe = exe_path
        self.workdir = workdir

    def run_match(self):
        start = time.time()
        try:
            subprocess.run([
                self.exe,
                "-p1", "chars/kfm/kfm.def",
                "-p2", "chars/BossForge/BossForge.def",
                "-p2.ai", "1",
                "-rounds", "2",
                "-s", "kfm.def"
            ], cwd=self.workdir, check=True)
        except Exception as e:
            print("[error] launching M.U.G.E.N.:", e)
        return max(0.01, time.time() - start)
