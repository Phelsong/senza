"""The senza compiler: minify and bundle pyScript client code.

Two jobs, webpack-style:

1. `minify_source` — safe AST-level minification of one module:
   - strips all docstrings (module, class, function), comments, and blank-line
     padding via `ast.parse` + `ast.unparse` (guaranteed syntax-correct output)
   - optionally drops `assert` statements (`--no-asserts` / `strip_asserts`)
   - does NOT rename identifiers or strip annotations (unsafe for dataclasses,
     pydantic, and the DOM APIs) — correctness over byte-count

2. `compile_tree` — walk the import graph from the app's entry modules so the
   dist contains exactly the modules reachable from the config's module list,
   each minified, keyed by their original relative path (pyScript fetches
   modules by path, so paths must be preserved).

The result is a dict of `{relative_path: minified_source}` — the caller decides
what to do with it (write a dist tree, write a tarball, serve directly).

Config handling (reading module lists, syncing `[files]`, interpreter pinning)
lives in `senza.config`.

CLI (from an app checkout):
    python senza/compiler.py <app-root> <config.toml> [--out dist] [--no-asserts] [--tar]
    python senza/compiler.py sync <app-root> <config.toml> [--dry-run]
"""

import ast
import shutil
import tarfile
from pathlib import Path
from typing import Optional, Union

StrPath = Union[str, Path]

# ----------------------------------------------------------------- minifier


class _DocstringStripper(ast.NodeTransformer):
    def _strip(self, node) -> None:
        body = getattr(node, "body", None)
        if body and len(body) > 0:
            first = body[0]
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                node.body = body[1:] or [ast.Pass()]

    def visit_Module(self, node):
        self.generic_visit(node)
        self._strip(node)
        return node

    def visit_ClassDef(self, node):
        self.generic_visit(node)
        self._strip(node)
        return node

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        self._strip(node)
        return node

    def visit_AsyncFunctionDef(self, node):
        self.generic_visit(node)
        self._strip(node)
        return node


class _AssertStripper(ast.NodeTransformer):
    def visit_Assert(self, node):
        return None


def minify_source(source: str, *, strip_asserts: bool = False) -> str:
    """Minify one Python module. Comments/docstrings/blanks gone, syntax kept."""
    tree = ast.parse(source)
    tree = _DocstringStripper().visit(tree)
    if strip_asserts:
        tree = _AssertStripper().visit(tree)
    ast.fix_missing_locations(tree)
    text = ast.unparse(tree)
    # collapse the blank-line padding unparse leaves between blocks
    return "\n".join(line for line in text.splitlines() if line.strip()) + "\n"


# ------------------------------------------------------------- import graph


def _resolve_imports(
    source: str,
    module_path: str,
    module_map: dict[str, Path],
    app_root: Optional[Path] = None,
    *,
    exclude: Optional[set[str]] = None,
) -> set[str]:
    """Relative paths of modules (in `module_map`, or existing .py files under
    `app_root`) that `source` imports.

    `exclude` is a set of leading directory prefixes to skip when resolving
    filesystem candidates — used to keep vendored runtime trees (e.g. the
    root `pyscript/` LSP symlink) out of app bundles."""
    found: set[str] = set()
    excluded = exclude or set()

    def allowed(candidate: str) -> bool:
        return not any(candidate.startswith(prefix) for prefix in excluded)

    tree = ast.parse(source)
    here = Path(module_path).parent
    for node in ast.walk(tree):
        names: list[str] = []
        level = 0
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            level = node.level or 0
            if node.module:
                names = [node.module]
            # from X import a, b  where X itself is a sibling module
            if level <= 1 and node.module and f"{here.as_posix()}/{node.module}.py" in module_map:
                found.add(f"{here.as_posix()}/{node.module}.py")
        base = here if level else Path(".")
        if level > 1:
            base = here
            for _ in range(level - 1):
                base = base.parent
        for name in names:
            pkg_parts = name.replace(".", "/")
            for candidate in (
                f"{base.as_posix()}/{pkg_parts}.py",
                f"{base.as_posix()}/{pkg_parts}/__init__.py",
            ):
                candidate = candidate.replace("./", "")
                if "" == candidate[:1] == "." or ".." in candidate.split("/"):
                    continue
                if candidate in module_map:
                    found.add(candidate)
                elif app_root is not None and allowed(candidate) and (app_root / candidate).is_file():
                    found.add(candidate)
    return found


def compile_tree(
    root: StrPath,
    files: list[str],
    *,
    strip_asserts: bool = False,
    include: Optional[list[str]] = None,
    exclude: Optional[set[str]] = None,
) -> dict[str, str]:
    """Compile `files` plus everything they transitively import (within the
    module map), rooted at `root`. Returns `{rel_path: minified_source}`.

    `exclude` prefixes skip filesystem-discovered candidates — used to keep
    vendored runtime trees (root `pyscript/` symlink etc.) out of bundles."""
    root = Path(root).resolve()
    wanted = {Path(f).as_posix() for f in files}
    for extra in include or []:
        wanted.add(Path(extra).as_posix())
    module_map: dict[str, Path] = {}
    for rel in wanted:
        p = root / rel
        if not p.is_file():
            raise FileNotFoundError(f"module not found: {rel} (root {root})")
        module_map[rel] = p
    # BFS over imports until closure
    queue = list(module_map)
    while queue:
        rel = queue.pop()
        imports = _resolve_imports(module_map[rel].read_text(), rel, module_map, root, exclude=exclude)
        for imported in imports:
            if imported not in module_map:
                module_map[imported] = root / imported
                queue.append(imported)
    out: dict[str, str] = {}
    for rel, path in sorted(module_map.items()):
        out[rel] = minify_source(path.read_text(), strip_asserts=strip_asserts)
    return out


def compile_config(
    app_root: StrPath,
    config_path: StrPath,
    *,
    strip_asserts: bool = False,
) -> dict[str, str]:
    """Convenience: compile the browser modules a pyScript config references.

    Both config styles are supported: legacy `[[fetch]]` sections and the
    modern `[files]` map (module discovery delegated to `senza.config`).
    """
    from senza.config import browser_module_paths

    return compile_tree(
        app_root,
        browser_module_paths(app_root, config_path, without_senza=True),
        strip_asserts=strip_asserts,
        # root vendored trees (LSP symlinks etc.) never belong in app bundles
        exclude={"pyscript/", "senza/"},
    )


# ----------------------------------------------------------------- CLI


def write_dist(
    compiled: dict[str, str],
    out_dir: StrPath,
    *,
    extra_files: Optional[dict[str, str]] = None,
) -> Path:
    out = Path(out_dir).resolve()
    if out.exists():
        shutil.rmtree(out)
    for rel, source in {**(extra_files or {}), **compiled}.items():
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source)
    return out


def tar_tree(tree_dir: StrPath, tar_path: StrPath) -> Path:
    tree_dir, tar_path = Path(tree_dir).resolve(), Path(tar_path).resolve()
    tar_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(tree_dir, arcname=tree_dir.name)
    return tar_path


def main(argv: Optional[list[str]] = None) -> None:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from senza import config as senza_config

    args = argv if argv is not None else sys.argv[1:]
    if args and args[0] == "sync":
        # usage: senza/compiler.py sync <app-root> <config.toml> [--dry-run]
        root, cfg = Path(args[1]), Path(args[2])
        dry = "--dry-run" in args

        def entries(path) -> list[str]:
            data = senza_config.load_config(path)
            if "files" in data:
                prefix = "{FROM}/"
                return [
                    s[len(prefix):] if s.startswith(prefix) else s.lstrip("/")
                    for s in data["files"]
                    if s != "{FROM}" and "{" not in s
                ]
            return [f for sec in data.get("fetch", []) for f in sec.get("files", [])]

        before = entries(cfg)
        after = senza_config.sync_files(root, cfg, write=not dry)
        diff = senza_config.files_changed(before, sorted(after))
        print(f"[{cfg}] {'(dry-run)' if dry else '(written)'}")
        for f in sorted(after):
            marker = "+ " if f in diff["added"] else (" - " if f in diff["removed"] else "   ")
            print(f"  {marker}{f}")
        return
    if len(args) < 2:
        print(__doc__)
        return
    root, cfg = Path(args[0]), Path(args[1])
    out_dir, tar_ball, strip = Path("dist"), False, False
    rest = args[2:]
    while rest:
        flag = rest.pop(0)
        if flag == "--out":
            out_dir = Path(rest.pop(0))
        elif flag == "--tar":
            tar_ball = True
        elif flag == "--no-asserts":
            strip = True
    compiled = compile_config(root, cfg / "web/config.toml" if cfg.is_dir() else cfg, strip_asserts=strip)
    dist = write_dist(compiled, out_dir)
    raw_total = sum(len((Path(root) / rel).read_bytes()) for rel in compiled)
    min_total = sum(len(s.encode()) for s in compiled.values())
    print(f"compiled {len(compiled)} modules -> {dist}")
    print(f"raw {raw_total:,}B -> minified {min_total:,}B ({min_total / max(raw_total, 1):.0%})")
    if tar_ball:
        print(f"tarball: {tar_tree(dist, dist.parent / f'client-dist-{config_hash(cfg)}.tar.gz')}")


def config_hash(config_path: StrPath) -> str:
    import hashlib

    data = Path(config_path).read_bytes()
    return hashlib.sha256(data).hexdigest()[:8]


if __name__ == "__main__":
    main()