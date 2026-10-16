"""Compile the app's sass entry. Defaults to sass/index.sass -> public/index.css."""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def compile_sass(source: str = "sass/index.sass", out: str = "public/index.css") -> None:
    command = ["sass","--no-source-map", str(ROOT / source), str(ROOT / out)]
    raise SystemExit(subprocess.call(command))


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        compile_sass(*args)
    elif len(args) == 0:
        compile_sass()
    else:
        print("usage: python senza/utils/compile_sass.py [source.sass out.css]")