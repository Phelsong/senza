"""Pin and optionally self-host the pyodide interpreter for pyScript apps.

State:
- `<app-root>/pyodide.version` — the pinned pyodide release (single source of
  truth; written here, read by `senza.config.interpreter_src`/`set_interpreter`)
- `<app-root>/packages/pyodide/<version>/full/` — the extracted release when
  self-hosting (the server must serve the `packages/` directory)

The config's `interpreter` key is then pinned via `senza.config.set_interpreter`,
pointing at the local copy when it exists and the jsdelivr CDN otherwise —
so dev/offline/self-hosted and prod deployments both work from one config.

CLI:
    python senza/utils/sync_pyodide.py check               # pinned vs upstream
    python senza/utils/sync_pyodide.py latest              # newest stable release
    python senza/utils/sync_pyodide.py pin latest [--root R] [--config C]
    python senza/utils/sync_pyodide.py pin 0.29.5 ...
    python senza/utils/sync_pyodide.py download [--core]   # fetch + extract (~6MB core / ~400MB full)
    python senza/utils/sync_pyodide.py status              # everything at a glance

`--config` also rewrites the config's `interpreter` key after pin/download.
"""

import json
import re
import shutil
import sys
import tarfile
import urllib.request
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from senza.config import (interpreter_src, load_config,  # noqa: E402
                          set_interpreter)

VERSION_FILE_NAME = "pyodide.version"
TAGS_URL = "https://api.github.com/repos/pyodide/pyodide/tags?per_page=100"
# plain semantic releases (0.x.y); excludes the python-3.14 experimentals (314.x.y)
_SEMVER = re.compile(r"^0\.\d+\.\d+$")


def _root(root: Optional[str]) -> Path:
    path = Path(root).resolve() if root else _discover()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _discover() -> Path:
    for candidate in (Path.cwd().resolve(), *Path.cwd().resolve().parents):
        if (candidate / VERSION_FILE_NAME).is_file():
            return candidate
    return Path.cwd().resolve()


def _version_file(root: Optional[str]) -> Path:
    return _root(root) / VERSION_FILE_NAME


# ------------------------------------------------------------------ versions


def pinned(root: Optional[str] = None) -> str:
    return _version_file(root).read_text().strip()


def set_pinned(version: str, root: Optional[str] = None) -> None:
    _version_file(root).write_text(f"{version.strip()}\n")


def upstream_tags() -> list[str]:
    req = urllib.request.Request(TAGS_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return [t["name"] for t in json.load(resp) if _SEMVER.match(t["name"])]


def latest() -> str:
    return upstream_tags()[0]


def download_dir(version: str, root: Optional[str]) -> Path:
    return _root(root) / "packages" / "pyodide" / version / "full"


def is_downloaded(version: str, root: Optional[str] = None) -> bool:
    return (download_dir(version, root) / "pyodide.mjs").is_file()


def check(root: Optional[str] = None) -> str:
    local = pinned(root)
    tags = upstream_tags()
    newest = tags[0]
    if local == newest:
        return f"up to date: {local} (== newest upstream)"
    if local in tags:
        newer = tags[: tags.index(local)]
        return f"outdated: pinned {local}, newest upstream {newest} ({len(newer)} newer)"
    return f"unknown: pinned {local} is not a published tag. Newest: {newest}"


def download(root: Optional[str] = None, version: Optional[str] = None, core: bool = False) -> Path:
    """Download and extract a pyodide release. `core` = interpreter only (~6MB);
    full adds the package repository (~400MB) for fully self-hosted installs."""
    version = version or pinned(root)
    target = download_dir(version, root)
    if (target / "pyodide.mjs").is_file():
        print(f"already downloaded: {target}")
        return target
    asset = f"pyodide-core-{version}.tar.bz2" if core else f"pyodide-{version}.tar.bz2"
    url = f"https://github.com/pyodide/pyodide/releases/download/{version}/{asset}"
    print(f"downloading {url} ...")
    target.mkdir(parents=True, exist_ok=True)
    archive = target / asset
    urllib.request.urlretrieve(url, archive)
    with tarfile.open(archive, "r:bz2") as tar:
        tar.extractall(target)
    archive.unlink()
    print(f"extracted -> {target}")
    return target


def status(root: Optional[str] = None) -> str:
    v = pinned(root)
    lines = [
        f"pinned pyodide: {v} ({check(root)})",
        f"local copy: {'yes' if is_downloaded(v, root) else 'no'}",
        f"interpreter url: {interpreter_src(v, root)}",
    ]
    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> None:
    args = list(argv if argv is not None else sys.argv[1:])
    root = _pop_arg(args, "--root")
    config_path = _pop_arg(args, "--config")
    core = "--core" in args
    args = [a for a in args if not a.startswith("--")]
    match args:
        case ["check"]:
            print(check(root))
        case ["latest"]:
            print(latest())
        case ["status"]:
            print(status(root))
        case ["pin", version]:
            if version == "latest":
                version = latest()
            if version not in upstream_tags():
                print(f"error: {version} is not a published pyodide release")
                sys.exit(1)
            if version == pinned(root):
                print(f"already pinned: {version}")
            else:
                previous = pinned(root)
                set_pinned(version, root)
                print(f"pinned {previous} -> {version}")
            if config_path:
                print(f"interpreter: {set_interpreter(config_path, version, root)}")
        case ["download"]:
            download(root, core=core)
            candidates = [config_path] if config_path else ["web/config.toml"]
            for candidate in candidates:
                if Path(candidate).is_file():
                    print(f"interpreter: {set_interpreter(candidate, pinned(root), root)}")
        case _:
            print(__doc__)


def _pop_arg(args: list[str], flag: str) -> Optional[str]:
    if flag in args:
        i = args.index(flag)
        value = args[i + 1]
        del args[i : i + 2]
        return value
    return None


if __name__ == "__main__":
    main()