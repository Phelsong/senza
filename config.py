"""pyscript app config utilities: load, dump, keep `files` in sync, pin the
interpreter. Framework-agnostic (used by any server that embeds pyScript).

Modern pyscript (2025.10+) defines browser modules via the `[files]` option —
source URL -> virtual-filesystem destination, with a mini templating language.
senza's convention (written by `sync_files`):

    version = "0.3.0"
    packages = ["orjson"]
    interpreter = "0.29.5"          # pyodide pin (see pyodide.version)

    [files]
    "{FROM}" = "/pyscript-source"   # the app's own source server
    "{FROM}/web/app.py" = "./web/app.py"
    "{FROM}/views/hello.py" = "./views/hello.py"

Legacy `[[fetch]]` sections (from ≤2024) are still readable: `sync_files`
migrates them into the `[files]` map automatically.

State files, at the app root:
- `pyscript.version` — pinned pyscript release (managed by senza/releases.py)
- `pyodide.version` — pinned pyodide release (managed by senza/utils/sync_pyodide.py)
"""

import re
import tomllib
from pathlib import Path
from typing import Any, Optional, Union

StrPath = Union[str, Path]
VERSION_FILE_NAME = "pyodide.version"


# ------------------------------------------------------------------ paths


def _discover_pin_file(root: Optional[StrPath], name: str) -> Path:
    """Explicit root, else scan upward from cwd (mirrors senza/releases.py)."""
    if root is not None:
        return Path(root).resolve() / name
    here = Path.cwd().resolve()
    for candidate in (here, *here.parents):
        if (candidate / name).is_file():
            return candidate / name
    return here / name


def pinned_pyodide(root: Optional[StrPath] = None) -> str:
    """The pinned pyodide release (e.g. '0.29.5'), read from pyodide.version."""
    return _discover_pin_file(root, VERSION_FILE_NAME).read_text().strip()


def set_pinned_pyodide(version: str, root: Optional[StrPath] = None) -> None:
    _discover_pin_file(root, VERSION_FILE_NAME).write_text(f"{version.strip()}\n")


# ------------------------------------------------------------------ TOML


def load_config(config_path: StrPath) -> dict:
    with open(config_path, "rb") as f:
        return tomllib.load(f)


def _toml_key(key: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_-]+", key):
        return key
    escaped = key.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list) and value and isinstance(value[0], dict):
        raise ValueError("array-of-tables handled by dump_config itself")
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(v) for v in value) + "]"
    if isinstance(value, dict):
        raise ValueError("nested dict value; put it in a [table]")
    raise ValueError(f"unsupported TOML value: {type(value).__name__} {value!r}")


def dump_config(config: dict, title: Optional[str] = None) -> str:
    """Serialize a pyscript-config-shaped dict to TOML text.

    Supports: top-level scalars, arrays of scalars (incl. `[[fetch]]` legacy
    array-of-tables), and `[table]` string maps (`[files]`). Output is always
    verified by re-parsing with tomllib: if it doesn't round-trip, we refuse
    to write.
    """
    lines: list[str] = []

    for key, value in config.items():
        if isinstance(value, dict) or (
            isinstance(value, list) and value and isinstance(value[0], dict)
        ):
            continue
        lines.append(f"{key} = {_toml_value(value)}")

    for key, value in config.items():
        if isinstance(value, dict):
            if lines:
                lines.append("")
            lines.append(f"[{_toml_key(key)}]")
            for sub_key, sub_value in value.items():
                lines.append(f"{_toml_key(sub_key)} = {_toml_value(sub_value)}")

    for key, value in config.items():
        if isinstance(value, list) and value and isinstance(value[0], dict):
            for table in value:
                if lines:
                    lines.append("")
                lines.append(f"[[{_toml_key(key)}]]")
                for sub_key, sub_value in table.items():
                    lines.append(f"{_toml_key(sub_key)} = {_toml_value(sub_value)}")

    text = "\n".join(lines) + "\n"
    if title:
        text = f"# {title}\n{text}"
    if tomllib.loads(text) != config:
        raise ValueError("TOML round-trip mismatch; refusing to write config")
    return text


def write_config(config: dict, config_path: StrPath) -> None:
    Path(config_path).write_text(dump_config(config))


# ------------------------------------------------------------- interpreter


def interpreter_src(pyodide_version: Optional[str] = None, root: Optional[StrPath] = None) -> str:
    """Self-hosted pyodide URL if downloaded (packages/pyodide/<v>/full),
    else the jsdelivr CDN for the pinned version."""
    version = pyodide_version or pinned_pyodide(root)
    local = Path(_discover_pin_file(root, VERSION_FILE_NAME)).parent
    if (local / "packages" / "pyodide" / version / "full" / "pyodide.mjs").is_file():
        return f"/packages/pyodide/{version}/full/pyodide.mjs"
    return f"https://cdn.jsdelivr.net/pyodide/v{version}/full/pyodide.mjs"


def set_interpreter(config_path: StrPath, pyodide_version: Optional[str] = None, root: Optional[StrPath] = None) -> str:
    """Pin `interpreter = ...` in the config to the resolved pyodide URL."""
    src = interpreter_src(pyodide_version, root)
    config = load_config(config_path)
    if config.get("interpreter") == src:
        return src
    config["interpreter"] = src
    write_config(config, config_path)
    return src


# -------------------------------------------------------------- files sync


def browser_module_paths(
    app_root: StrPath, config_path: StrPath, *, senza_only: bool = False, without_senza: bool = False
) -> list[str]:
    """Relative paths of enabled browser modules a config references, in both
    config styles. By default everything; `senza_only=True` gets just the
    senza modules (they are schema-served unminified from packages);
    `without_senza=True` gets just app modules (compiled by the compiler)."""
    app_root = Path(app_root).resolve()
    config = load_config(config_path)
    rels: list[str] = []
    if "files" in config:
        prefix = "{FROM}/"
        senza_prefix = "{SENZA}/"
        for src in config["files"]:
            is_senza = src.startswith(senza_prefix)
            if src in ("{FROM}", "{SENZA}") or ("{" in src and not (src.startswith(prefix) or is_senza)):
                continue
            rel = (
                src[len(prefix):]
                if src.startswith(prefix)
                else src[len(senza_prefix):]
                if is_senza
                else src.lstrip("/")
            )
            rel = rel.replace("senza/", "", 1) if is_senza else rel
            rel = f"senza/{rel}" if is_senza and not rel.startswith("senza/") else rel
            if not rel.endswith(".py"):
                continue
            if is_senza:
                if senza_only and (app_root / "packages" / rel).is_file():
                    rels.append(rel)
            elif senza_only:
                continue
            elif without_senza:
                if (app_root / rel).is_file():
                    rels.append(rel)
            else:
                if (app_root / rel).is_file():
                    rels.append(rel)
    else:  # legacy [[fetch]]
        for section in config.get("fetch", []):
            for rel in section.get("files", []):
                if rel.endswith(".py") and rel != "web/config.toml" and (app_root / rel).is_file():
                    rels.append(rel)
    return rels


def _legacy_to_files(config: dict) -> bool:
    """True if the config still uses legacy `[[fetch]]` (migrate on sync)."""
    return "fetch" in config and "files" not in config


def _migrate_legacy(config: dict) -> None:
    """Convert `[[fetch]] from/files` into the modern `[files]` map."""
    from_url = "/pyscript-source"
    mapping: dict[str, str] = {"{FROM}": from_url}
    for section in config.get("fetch", []):
        from_url = section.get("from", from_url)
        mapping["{FROM}"] = from_url
        for rel in section.get("files", []):
            if rel.endswith(".toml") and rel == "web/config.toml" or rel.endswith(".toml"):
                continue  # config files aren't VFS modules
            if not rel.endswith(".py"):
                continue
            mapping[f"{{FROM}}/{rel}"] = f"./{rel}"
    config.pop("fetch")
    config["files"] = mapping


def _resolve_from(files_map: dict[str, str]) -> str:
    return files_map.get("{FROM}", "/pyscript-source")


def sync_files(
    app_root: StrPath,
    config_path: StrPath,
    *,
    write: bool = True,
) -> dict[str, str]:
    """Keep the config's `[files]` browser-module map in sync with the code.

    - keeps every existing entry in its original order
    - drops entries whose source file no longer exists
    - adds every `.py` module reachable via the import graph from the kept
      modules (so newly created views register by being imported once)

    Migrates legacy `[[fetch]]` configs in the same pass. Returns the final
    `{rel_path: source_url}` map for reporting.
    """
    from senza import compiler  # local import avoids a config<->compiler cycle

    app_root, config_path = Path(app_root).resolve(), Path(config_path)
    config = load_config(config_path)
    if _legacy_to_files(config):
        _migrate_legacy(config)

    files_map = config.get("files", {})
    from_url = _resolve_from(files_map)
    prefix = f"{{FROM}}/"
    senza_prefix = f"{{SENZA}}/"

    # pass 1: keep entries that still exist; dests mirror the relative path
    # so package imports keep working. senza entries are checked against the
    # packages copy (they're served from there, not from the checkout).
    kept: dict[str, str] = {}
    report: dict[str, str] = {}
    for src, dest in files_map.items():
        if src in ("{FROM}", "{SENZA}"):
            continue
        if src.startswith(f"{prefix}pyscript/"):
            # root LSP symlink resolved as an import: never an app module
            continue
        if src.startswith(senza_prefix):  # senza served from packages/senza
            rel = src[len(senza_prefix):]
            if (app_root / "packages" / rel).is_file():
                kept[src] = dest
                report[rel] = f"/packages/{rel}"
            continue
        if src.startswith(prefix):
            rel = src[len(prefix):]
        elif "{" not in src:  # literal source entries stay untouched
            rel = src.lstrip("/")
        else:  # unknown placeholder / malformed: leave untouched
            kept[src] = dest
            continue
        if (app_root / rel).is_file():
            kept[f"{prefix}{rel}"] = f"./{rel}"
            report[rel] = f"{from_url}/{rel}"

    # pass 2: discover imports of the kept modules
    discovered: set[str] = set()
    seeds = [rel for rel in report if rel.endswith(".py")]
    if seeds:
        compiled = compiler.compile_tree(
            app_root,
            seeds,
            # root vendored trees (LSP symlinks etc.) are never app modules
            exclude={"pyscript/", "senza/"},
        )
        discovered = set(compiled) - set(report)

    # definitions must precede their uses for pyscript's files templating
    new_map: dict[str, str] = {}
    if files_map.get("{SENZA}"):
        new_map["{SENZA}"] = files_map["{SENZA}"]
    new_map["{FROM}"] = from_url
    new_map.update(kept)
    for rel in sorted(discovered):
        new_map[f"{prefix}{rel}"] = f"./{rel}"
        report[rel] = f"{from_url}/{rel}"

    config["files"] = new_map
    if write:
        write_config(config, config_path)
    return report


def files_changed(old: list[str], new: list[str]) -> dict[str, list[str]]:
    """Diff helper for reporting what a sync would change."""
    return {
        "added": [f for f in new if f not in old],
        "removed": [f for f in old if f not in new],
    }