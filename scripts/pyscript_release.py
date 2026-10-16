"""CLI for managing this app's pyscript release pin.

Delegates to the framework-agnostic library in senza core (senza/releases.py).

Usage (same as the library CLI):
    python scripts/pyscript_release.py check         # compare pinned vs upstream
    python scripts/pyscript_release.py latest        # print newest release
    python scripts/pyscript_release.py pin latest    # pin newest + log it
    python scripts/pyscript_release.py pin 2026.7.3  # pin an exact version
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from senza.releases import main  # noqa: E402
from utils import project_root  # noqa: E402

if __name__ == "__main__":
    args = sys.argv[1:]
    try:
        main([*args, "--root", project_root])
    except ValueError as err:
        print(f"error: {err}")
        sys.exit(1)