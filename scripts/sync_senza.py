"""Keep the browser-side senza modules in place, independently of the checkout.

The app serves senza from its own copy at `<app-root>/packages/senza/` (LSP
points there too). The app's config references them through their own
placeholder so they stay servable even while the senza checkout is being
updated, switched, or absent:

    [files]
    "{SENZA}" = "/packages"
    "{SENZA}/senza/router.py" = "./senza/router.py"

    # app modules stay with the app's own source server
    "{FROM}" = "/pyscript-source"
    "{FROM}/web/app.py" = "./web/app.py"

What this does:
1. copies the browser-facing senza modules from a senza checkout
   (default `<app_root>/senza`, or `--from <dir>`) into
   `<app-root>/packages/senza/`
2. rewrites `[files]`: senza entries under `{FROM}` (or the legacy
   `[[fetch]]` list) move under `{SENZA}` pointing at the packages copy

CLI:
    python senza/sync_senza.py <app-root> [--from <senza-checkout>]
"""

import sys
from pathlib import Path
from typing import Optional, Union

StrPath = Union[str, Path]
# senza modules the browser needs — keep in lockstep with senza's public surface
BROWSER_MODULES = ["router.py", "visibility.py"]
SENZA_PLACEHOLDER = "{SENZA}"
SENZA_PACKAGES_DIR = "packages/senza"
SENZA_FROM_URL = "/packages"
FROM_PLACEHOLDER = "{FROM}"


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


def sync(
    app_root: StrPath,
    senza_dir: Optional[StrPath] = None,
    *,
    config_path: Optional[StrPath] = None,
) -> dict[str, dict[str, str]]:
    """Copy senza browser modules into packages and migrate the config.

    Returns `{"copied": {rel: dest}, "config": {src_key: dest}}` for reporting.
    """
    _import_senza()
    from senza.config import load_config, write_config

    root = Path(app_root).resolve()
    senza_dir = Path(senza_dir).resolve() if senza_dir else root / "senza"
    config_path = Path(config_path).resolve() if config_path else root / "web" / "config.toml"

    copied: dict[str, str] = {}
    for rel in BROWSER_MODULES:
        source = senza_dir / rel
        if not source.is_file():
            raise FileNotFoundError(f"senza checkout missing {rel} (looked in {senza_dir})")
        target = root / SENZA_PACKAGES_DIR / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text())
        copied[f"senza/{rel}"] = target.as_posix()

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
        if moved:
            new_map: dict[str, str] = {SENZA_PLACEHOLDER: files_map.get(SENZA_PLACEHOLDER, SENZA_FROM_URL)}
            for src, dest in files_map.items():
                new_map.setdefault(src, dest)
            new_map[FROM_PLACEHOLDER] = files_map.get(FROM_PLACEHOLDER, "/pyscript-source")
            for src, dest in moved.items():
                new_map[src] = dest
            cfg["files"] = new_map
            write_config(cfg, config_path)
            config = moved

        elif cfg.get("files") and SENZA_PLACEHOLDER not in cfg["files"]:
            # ensure the {SENZA} definition exists even when nothing moved
            cfg["files"] = {SENZA_PLACEHOLDER: SENZA_FROM_URL, **cfg["files"]}
            write_config(cfg, config_path)

    return {"copied": copied, "config": config}


def main() -> None:
    args = list(sys.argv[1:])
    root = args[0] if args and not args[0].startswith("--") else "."
    without = "--from" in args
    senza_dir = args[args.index("--from") + 1] if without else None
    report = sync(root, senza_dir)
    for rel, dest in report["copied"].items():
        print(f"copied {rel} -> {dest}")
    for src, dest in report["config"].items():
        print(f'config: {src} = "{dest}"')

    print("add to pixi tasks: \n")
    print("""
    # senza core scripts
    sync-config = "python senza/scripts/sync_web_config.py ."
    sync-senza = "python senza/scripts/sync_senza.py ."
    compile-dist = "python senza/scripts/compile_dist.py ."
    compile_sass = { cmd = 'python senza/scripts/compile_sass.py {{ source }} {{ out }}', args = [
      { arg = "source", default = "sass/index.scss" },
      { arg = "out", default = "public/index.css" },
    ] }
    sync-pyodide = "python senza/scripts/sync_pyodide.py status"
    sync-pyodide-check = "python senza/scripts/sync_pyodide.py check"
    sync-pyodide-latest = "python senza/scripts/sync_pyodide.py latest"
    sync-pyodide-pin = { cmd = "python senza/scripts/sync_pyodide.py pin {{ version }}", args = [
      { arg = "version", default = "latest" },
    ] }
    sync-pyodide-download = { cmd = "python senza/scripts/sync_pyodide.py download {{ version }}", args = [
      { arg = "version", default = "" },
    ] }
    sync-pyodide-download-core = "python senza/scripts/sync_pyodide.py download --core"
    sync-lsp = "python senza/scripts/sync_pyscript_lsp.py ."
    pyscript-check = "python senza/releases.py check --root ."
    pyscript-pin = { cmd = "python senza/releases.py pin {{ version }} --root .", args = [
      { arg = "version", default = "latest" },
    ] }""")

if __name__ == "__main__":
    main()