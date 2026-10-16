"""PyScript release pinning for apps that embed pyScript.

Library **and** CLI, framework-agnostic: usable from FastAPI, Flask, static
sites, or its own command line. State lives in two files:

- `<project_root>/pyscript.version` — the pinned release the app's shell
  templates/renderers read at runtime
- `senza/releases.txt` (next to this file) — the running history of pinned
  releases; every successful pin change appends its snippet there

Library use:
    from senza.releases import pinned, check, pin, core_js

    pinned("/path/to/app")          # e.g. "2026.7.3"
    core_js()                       # CDN url for the pinned release
    check("/path/to/app")           # "up to date: ..." report
    pin("latest", "/path/to/app")   # pin newest upstream + log it

CLI (from an app checkout that has pyscript.version, or pass --root):
    python senza/releases.py check
    python senza/releases.py latest
    python senza/releases.py pin latest
    python senza/releases.py pin 2026.7.3 --root /path/to/app

The project root is found by scanning upward from the cwd for a
`pyscript.version` file, so running the CLI inside an app checkout needs no
flags.
"""

import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Optional

VERSION_FILE_NAME = "pyscript.version"
RELEASES_LOG_NAME = "releases.txt"
RELEASES_LOG = Path(__file__).resolve().parent / RELEASES_LOG_NAME
TAGS_URL = "https://api.github.com/repos/pyscript/pyscript/tags?per_page=30"


# ----------------------------------------------------------------- paths


def _root(project_root: Optional[str] = None) -> Path:
    """Resolve the app root: explicit arg, else scan upward from cwd."""
    if project_root is not None:
        return Path(project_root).resolve()
    here = Path(os.getcwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / VERSION_FILE_NAME).is_file():
            return candidate
    return here  # fall back to cwd (caller gets a clear error on read)


def _version_file(project_root: Optional[str] = None) -> Path:
    return _root(project_root) / VERSION_FILE_NAME


# ----------------------------------------------------------------- read/write


def pinned(project_root: Optional[str] = None) -> str:
    """The currently pinned pyScript release, e.g. '2026.7.3'."""
    return _version_file(project_root).read_text().strip()


def set_pinned(version: str, project_root: Optional[str] = None) -> None:
    _version_file(project_root).write_text(f"{version.strip()}\n")


def core_css(version: Optional[str] = None) -> str:
    """CDN URL of the pinned core.css."""
    return f"https://pyscript.net/releases/{version or pinned()}/core.css"


def core_js(version: Optional[str] = None) -> str:
    """CDN URL of the pinned core.js."""
    return f"https://pyscript.net/releases/{version or pinned()}/core.js"


def shell_tags(version: Optional[str] = None) -> str:
    """The two HTML tags for a page head: core.css link + core.js script."""
    return (
        f'<link rel="stylesheet" href="{core_css(version)}" />\n'
        f'<script type="module" src="{core_js(version)}"></script>'
    )


def log_release(version: str) -> None:
    """Append the snippet for `version` to the senza release history log."""
    snippet = f"\n# {version}\n{shell_tags(version)}\n"
    with open(RELEASES_LOG, "a") as f:
        f.write(snippet)


# ----------------------------------------------------------------- upstream


def upstream_tags() -> list[str]:
    """Release tags published on pyscript/pyscript, newest first."""
    req = urllib.request.Request(TAGS_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return [tag["name"] for tag in json.load(resp)]


def latest() -> str:
    return upstream_tags()[0]


def check(project_root: Optional[str] = None) -> str:
    """Report comparing the pinned release to upstream."""
    local = pinned(project_root)
    tags = upstream_tags()
    newest = tags[0]
    if local == newest:
        return f"up to date: {local} (== newest upstream)"
    if local in tags:
        newer = tags[: tags.index(local)]
        preview = ", ".join(newer[:5]) + ("..." if len(newer) > 5 else "")
        return f"outdated: pinned {local}, newest upstream {newest} ({len(newer)} newer: {preview})"
    return f"unknown: pinned {local} is not a published tag. Newest: {newest}"


def pin(version: str, project_root: Optional[str] = None) -> str:
    """Pin a release ('2026.7.3' or 'latest'), validate it, and log it."""
    if version == "latest":
        version = latest()
    if version not in upstream_tags():
        raise ValueError(f"{version} is not a published pyScript release tag")
    previous = pinned(project_root)
    if version == previous:
        print(f"already pinned: {version}")
        return version
    set_pinned(version, project_root)
    log_release(version)
    print(f"pinned {previous} -> {version} (logged to {RELEASES_LOG})")
    return version


# ----------------------------------------------------------------- CLI


def main(argv: Optional[list[str]] = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    root: Optional[str] = None
    if "--root" in args:
        i = args.index("--root")
        root = args[i + 1]
        args = args[:i] + args[i + 2 :]
    match args:
        case ["check"]:
            print(check(root))
        case ["latest"]:
            print(latest())
        case ["pin", version]:
            pin(version, root)
        case _:
            print(__doc__)


if __name__ == "__main__":
    main()