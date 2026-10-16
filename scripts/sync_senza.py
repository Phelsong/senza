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
  the core modules into `packages/senza/`, and record the tag in
  `<app-root>/senza.version` — that pin keeps subsequent pulls reproducible
- `--pin <tag|latest>`: resolve and use a specific release (writing the pin)
- `--from <dir>`: dev mode — no network, copy a senza checkout instead

CLI:
    python senza/scripts/sync_senza.py <app-root> [--pin <tag|latest>] [--from <dir>]
"""

import io
import sys
import zipfile
from pathlib import Path
from typing import Optional, Union
import urllib.request

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
            raise ValueError(f"{want} is not a published {REPO} release; available: {', '.join(tags[:5])}")
        return want
    return pinned(root) or tags[0]


def pull(
    root: StrPath,
    tag: str,
    *,
    record: bool = True,
) -> dict[str, str]:
    """Download the release zipball, extract core modules into
    `packages/senza/` (top-level library files only), and mark the version.
    Returns `{name: dest}` for reporting."""
    root = Path(root).resolve()
    target = root / SENZA_PACKAGES_DIR
    target.mkdir(parents=True, exist_ok=True)

    request = urllib.request.Request(ZIPBALL_URL + tag, headers={"Accept": "application/zip"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()

    copied: dict[str, str] = {}
    with zipfile.ZipFile(io.BytesIO(data)) as bundle:
        for entry in bundle.namelist():
            if entry.endswith("/"):
                continue
            first, _, rest = entry.partition("/")
            if not first or not rest or "/" in rest or rest.startswith("."):
                continue  # subdirectories and dotfiles stay in the repo
            member = bundle.read(entry)
            dest = target / rest
            dest.write_bytes(member)
            copied[rest] = dest.as_posix()

    (target / ".version").write_text(f"{tag}\n")
    if record or pinned(root):
        set_pinned(tag, root)
    return copied

# ------------------------------------------------------------ packages sync


def sync(
    root: StrPath,
    *,
    pin: Optional[str] = None,
    senza_dir: Optional[StrPath] = None,
    config_path: Optional[StrPath] = None,
) -> dict[str, dict[str, str]]:
    """Refresh `packages/senza` (from a release by default, a checkout with
    `--from`) and migrate the config's senza entries under `{SENZA}`.

    Returns `{"source": mode, "copied": {name: dest}, "config": {src: dest}}`.
    """
    _import_senza()
    from senza.config import load_config, write_config

    root = Path(root)
    config_path = Path(config_path).resolve() if config_path else root / "web" / "config.toml"

    copied: dict[str, str] = {}
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
        copied = pull(root, tag)
        source_mode = f"release {tag}"

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
            new_map: dict[str, str] = {SENZA_PLACEHOLDER: files_map.get(SENZA_PLACEHOLDER, SENZA_FROM_URL)}
            for src, dest in files_map.items():
                new_map.setdefault(src, dest)
            new_map[FROM_PLACEHOLDER] = files_map.get(FROM_PLACEHOLDER, "/pyscript-source")
            for src, dest in moved.items():
                new_map[src] = dest
            cfg["files"] = new_map
            write_config(cfg, config_path)
            config = moved

    return {"source": source_mode, "copied": copied, "config": config}


def main() -> None:
    args = list(sys.argv[1:])
    root = args[0] if args and not args[0].startswith("--") else "."
    pin: Optional[str] = None
    senza_dir: Optional[str] = None
    if "--from" in args:
        i = args.index("--from")
        senza_dir = args[i + 1]
        del args[i : i+2]
    if "--pin" in args:
        i = args.index("--pin")
        pin = args[i + 1]
        del args[i : i+2]
    report = sync(root, pin=pin, senza_dir=senza_dir)
    print(f"senza source: {report['source']}")
    for name, dest in report["copied"].items():
        print(f"  {name} -> {dest}")
    for src, dest in report["config"].items():
        print(f'config: {src} = "{dest}"')


if __name__ == "__main__":
    main()
