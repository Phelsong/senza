"""Keep an app's pyscript config `[files]` map in sync with its code.

Generic senza tool — works in any app directory:

    python senza/sync_web_config.py <app-root> [--dry-run]

- newly imported browser modules (imported once from the entry) are added
- entries whose file (or packages copy) disappeared are dropped
- legacy `[[fetch]]` configs are migrated to the modern `[files]` format

NOTE: source allowlist routers (e.g. routers/pyscript_source.py) build their
allowlist at startup — restart after a real run.
"""

import sys
from pathlib import Path


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


_import_senza()
from senza import config as senza_config  # noqa: E402

CONFIG = "web/config.toml"


def entries(config_path: Path) -> list[str]:
    config = senza_config.load_config(config_path)
    if "files" in config:
        out = []
        for src in config["files"]:
            if src in ("{FROM}", "{SENZA}"):
                continue
            if src.startswith("{FROM}/"):
                out.append(src[len("{FROM}/"):])
            elif src.startswith("{SENZA}/"):
                out.append(src[len("{SENZA}/"):])
            elif "{" not in src:
                out.append(src.lstrip("/"))
        return out
    return [f for sec in config.get("fetch", []) for f in sec.get("files", [])]


def main() -> None:
    argv = sys.argv[1:]
    root = argv[0] if argv and not argv[0].startswith("--") else "."
    dry = "--dry-run" in argv
    config_path = Path(root).resolve() / CONFIG
    before = entries(config_path)
    after = senza_config.sync_files(root, config_path, write=not dry)
    diff = senza_config.files_changed(before, sorted(after))
    print(f"[{config_path.name}] {'(dry-run)' if dry else '(written)'}")
    for f in sorted(after):
        marker = "+ " if f in diff["added"] else ("- " if f in diff["removed"] else "  ")
        print(f"  {marker}{f}")


if __name__ == "__main__":
    main()
