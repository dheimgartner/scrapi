from pathlib import Path
import subprocess
import sys

APP_PATH = Path(__file__).parent / "app.py"


def gui() -> None:
    """GUI-tool"""
    cmd = [sys.executable, "-m", "chainlit", "run", str(APP_PATH)]
    subprocess.run(cmd, check=True)
