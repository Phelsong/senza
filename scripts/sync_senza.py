"""Populate the app's served/LSP copy of senza from a Phelsong/senza release.

The app serves senza from its own copy at `<app-root>/packages/senza/` (LSP
points there too). The app's config references them through their own
placeholder so they stay servable independently of any checkout:

    [files]
    "{SENZA}" = "/packages"
    "{SENZA}/senza/router.py" = "./senza/router.py"

    # app modules stay with the app's own source server
    "{FROM}" = "/pyscript-source"
    "{FROM}/web/app.py" = "./web/app.py"

Modes:
- default: pull the latest Phelsong/senza GitHub release (zipball), extract
  the core modules into `packages/senza/`, refresh the app's root `senza/`
  directory from the same bundle, and record the tag in
  `<app-root>/senza.version` — that pin keeps subsequent pulls reproducible
- `--pin <tag|latest>`: resolve and use a specific release (writing the pin)
- `--from <dir>`: dev mode — no network, copy a senza checkout instead
- `--skip-root`: refresh `packages/` only, leave the root `senza/` alone
- `--refresh-scripts`: also let the release overwrite the local script suite
  (default OFF — without it the running sync script can never be clobbered
  by a release whose scripts are older, so the root refresh keeps working
  across runs even before a newer release publishes this very script)

CLI:
    python senza/scripts/sync_senza.py <app-root> [--pin <tag|latest>] [--from <dir>]
                                        [--skip-root] [--refresh-scripts]
"""

import io
import sys
import zipfile
from pathlib import Path
from typing import Optional, Union
import urllib.request
import urllib.error

sys.path.insert(0, str(Path(__file__).resolve().parent))

StrPath = Union[str, Path]
REPO = "Phelsong/senza"
RELEASES_URL = f"https://api.github.com/repos/{REPO}/releases?per_page=100"
ZIPBALL_URL = f"https://api.github.com/repos/{REPO}/zipball/"
SENZA_PLACEHOLDER = "{SENZA}"
SENZA_PACKAGES_DIR = "packages/senza"
SENZA_FROM_URL = "/packages"
FROM_PLACEHOLDER = "{FROM}"
# dev-mode fallback: which senza files land in packages from a plain checkout
BROWSER_MODULES = ["router.py", "visibility.py"]

SENZA_PIN_FILE = "senza.version"
THIS_FILE = "scripts/sync_senza.py"

_root_suffixes = frozenset({".py", ".md", ".toml", ".txt"})
_root_files = frozenset({"LICENSE"})
_root_dirs = frozenset({"scripts"})


def _import_senza():
    """Make `senza` importable whether we run from an app root or from the
    core checkout itself."""
    here = Path(__file__).resolve()
    for candidate in (Path.cwd().resolve(), here.parents[1]):
        if (candidate / "senza" / "config.py").is_file():
            if str(candidate) not in sys.path:
                sys.path.insert(0, str(candidate))
            return
    raise ModuleNotFoundError("no senza/ package in cwd or alongside this script")


# ------------------------------------------------------------------ pinning


def pinned(root: StrPath) -> Optional[str]:
    """The pinned senza release tag from `<app-root>/senza.version`, if any."""
    file = Path(root) / SENZA_PIN_FILE
    return file.read_text().strip() if file.is_file() else None


def set_pinned(tag: str, root: StrPath) -> None:
    (Path(root) / SENZA_PIN_FILE).write_text(f"{tag.strip()}\n")


def upstream_tags() -> list[str]:
    import json

    request = urllib.request.Request(RELEASES_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        releases = json.load(response)
    tags = [r["tag_name"] for r in releases if not r.get("draft") and not r.get("prerelease")]
    if not tags:
        raise RuntimeError(
            f"no published releases on github.com/{REPO} — create one "
            f"(e.g. `gh release create 1.0.0`) so apps can pull senza"
        )
    return tags


def resolve_tag(root: StrPath, want: Optional[str] = None) -> str:
    """`want` is 'latest', an explicit tag, or None (use the pin, else latest)."""
    tags = upstream_tags()
    if want and want != "latest":
        if want not in tags:
            raise ValueError(
                f"{want} is not a published {REPO} release; available: {', '.join(tags[:5])}"
            )
        return want
    return pinned(root) or tags[0]


def _wants(rel: str) -> bool:
    rel = rel.strip("/")
    if rel.startswith("."):
        return False
    if "/" in rel:
        first, _, rest = rel.partition("/")
        return first in _root_dirs and bool(rest)
    if Path(rel).suffix in _root_suffixes:
        return True
    return Path(rel).name in _root_files


def pull(
    root: StrPath,
    tag: str,
    *,
    record: bool = True,
    rel_content: Optional[dict[str, bytes]] = None,
) -> dict[str, str]:
    """Download the release zipball. Extract top-level library files into
    `packages/senza/` (marked with the version). When `rel_content` is passed,
    every non-dotfile release path is collected there for the caller (used
    for the app-root senza refresh). Returns `{name: dest}`."""
    root = Path(root).resolve()
    target = root / SENZA_PACKAGES_DIR
    target.mkdir(parents=True, exist_ok=True)
    if rel_content is None:
        rel_content = {}

    request = urllib.request.Request(ZIPBALL_URL + tag, headers={"Accept": "application/zip"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()

    copied: dict[str, str] = {}
    with zipfile.ZipFile(io.BytesIO(data)) as bundle:
        for entry in bundle.namelist():
            if entry.endswith("/"):
                continue
            first, _, rest = entry.partition("/")
            if not first or not rest or rest.startswith("."):
                continue
            member = bundle.read(entry)
            rel_content[rest] = member
            if "/" not in rest:
                dest = target / rest
                dest.write_bytes(member)
                copied[rest] = dest.as_posix()

    (target / ".version").write_text(f"{tag}\n")
    if record or pinned(root):
        set_pinned(tag, root)
    return copied


def update_root_dir(
    root: StrPath,
    rel_content: dict[str, bytes],
    *,
    refresh_scripts: bool = False,
    self_path: str = THIS_FILE,
) -> dict[str, str]:
    """Write the release's core files into `<app-root>/senza/` (the downstream
    app's local senza copy — a workspace, submodule checkout, or fresh dir).
    Only updates paths present in the release; nothing is deleted.

    The RUNNING script (`scripts/sync_senza.py`) is never overwritten unless
    `refresh_scripts` is set — a release whose script is older than the one
    running would otherwise silently regress the root-refresh feature.

    Returns `{rel: dest}`."""
    root = Path(root)
    senza_root = root / "senza"
    senza_root.mkdir(parents=True, exist_ok=True)

    updated: dict[str, str] = {}
    for rel, data in rel_content.items():
        key = rel.strip("/")
        if not _wants(key):
            continue
        if key == self_path and not refresh_scripts:
            continue  # never clobber the running script by default
        dest = senza_root / key
        if dest.is_file() and dest.read_bytes() == data:
            continue  # unchanged
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        updated[key] = dest.as_posix()

    if updated:
        if (senza_root / ".git").exists():
            print(
                f"root senza updated ({len(updated)} files) — senza/ is a git "
                "submodule or checkout; commit these on the senza side"
            )
        else:
            print(f"root senza updated ({len(updated)} files)")
    return updated


def sync(
    root: StrPath,
    *,
    pin: Optional[str] = None,
    senza_dir: Optional[StrPath] = None,
    config_path: Optional[StrPath] = None,
    skip_root: bool = False,
    refresh_scripts: bool = False,
) -> dict[str, dict[str, str]]:
    """Refresh `packages/senza` (from a release by default, a checkout with
    `--from`), refresh the app's root `senza/`, and migrate the config's
    senza entries under `{SENZA}`.

    Returns `{"source": mode, "copied": {name: dest}, "root": {rel: dest},
    "config": {src: dest}}`.
    """
    _import_senza()
    from senza.config import load_config, write_config

    root = Path(root)
    config_path = Path(config_path).resolve() if config_path else root / "web" / "config.toml"

    copied: dict[str, str] = {}
    root_updated: dict[str, str] = {}
    if senza_dir is not None:  # dev mode: copy from a local checkout
        senza_root = Path(senza_dir).resolve()
        target = root / SENZA_PACKAGES_DIR
        target.mkdir(parents=True, exist_ok=True)
        for rel in BROWSER_MODULES:
            source = senza_root / rel
            if not source.is_file():
                raise FileNotFoundError(f"senza checkout missing {rel} (looked in {senza_root})")
            dest = target / rel
            dest.write_text(source.read_text())
            copied[rel] = dest.as_posix()
        source_mode = f"checkout {senza_root}"
    else:
        tag = resolve_tag(root, pin)
        rel_content: dict[str, bytes] = {}
        copied = pull(root, tag, rel_content=rel_content)
        source_mode = f"release {tag}"
        if not skip_root:
            root_updated = update_root_dir(
                root, rel_content, refresh_scripts=refresh_scripts
            ) or {}

    config: dict[str, str] = {}
    if config_path.is_file():
        cfg = load_config(config_path)
        if "fetch" in cfg:  # legacy: migrate to [files] first
            from senza.config import sync_files

            sync_files(root, config_path)
            cfg = load_config(config_path)
        files_map = dict(cfg.get("files", {}))

        moved: dict[str, str] = {}
        for src in list(files_map):
            if src.startswith(f"{FROM_PLACEHOLDER}/senza/"):
                rel = src[len(f"{FROM_PLACEHOLDER}/"):]  # senza/router.py
                moved[f"{SENZA_PLACEHOLDER}/{rel}"] = f"./{rel}"
                files_map.pop(src)

        needs_def = SENZA_PLACEHOLDER not in files_map and (
            moved or any(src.startswith(SENZA_PLACEHOLDER + "/") for src in files_map)
        )
        if moved or needs_def:
            # definitions precede their uses (pyscript's files templating)
            new_map: dict[str, str] = {
                SENZA_PLACEHOLDER: files_map.get(SENZA_PLACEHOLDER, SENZA_FROM_URL)
            }
            for src, dest in files_map.items():
                new_map.setdefault(src, dest)
            new_map[FROM_PLACEHOLDER] = files_map.get(FROM_PLACEHOLDER, "/pyscript-source")
            for src, dest in moved.items():
                new_map[src] = dest
            cfg["files"] = new_map
            write_config(cfg, config_path)
            config = moved

    return {"source": source_mode, "copied": copied, "root": root_updated, "config": config}


def main() -> None:
    args = list(sys.argv[1:])
    root = args[0] if args and not args[0].startswith("--") else "."
    pin: Optional[str] = None
    senza_dir: Optional[str] = None
    skip_root = "--skip-root" in args
    refresh_scripts = "--refresh-scripts" in args
    if "--from" in args:
        i = args.index("--from")
        senza_dir = args[i + 1]
        del args[i : i + 2]
    if "--pin" in args:
        i = args.index("--pin")
        pin = args[i + 1]
        del args[i : i + 2]

    report = sync(
        root,
        pin=pin,
        senza_dir=senza_dir,
        skip_root=skip_root,
        refresh_scripts=refresh_scripts,
    )
    print(f"senza source: {report['source']}")
    for name, dest in report["copied"].items():
        print(f"  {name} -> {dest}")
    for rel, dest in report.get("root", {}).items():
        print(f"root senza: {rel} -> {dest}")
    for src, dest in report["config"].items():
        print(f'config: {src} = "{dest}"')


if __name__ == "__main__":
    main()