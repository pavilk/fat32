import subprocess
import sys
from pathlib import Path


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def test_cli_ls(fat_image):
    img_path = Path(fat_image)
    fattool_path = Path(__file__).parent.parent / "fattool.py"

    res = run([
        sys.executable,
        str(fattool_path.resolve()),
        "-i", str(img_path),
        "ls",
        "/"
    ])

    assert res.returncode == 2, f"stdout: {res.stdout}\nstderr: {res.stderr}"
    assert res.stdout is not None
