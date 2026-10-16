"""Build an app's minified client dist (generic senza tool).

    python senza/compile_dist.py <app-root> [--tar] [--no-asserts]

Compiles exactly the app modules the config references (senza modules are
served as-is from packages/senza) into `<app-root>/dist/pyscript/`; in
PRODUCTION a source allowlist router serves these instead of raw sources.
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
from senza import compiler, releases  # noqa: E402


def main() -> None:
    argv = sys.argv[1:]
    root = Path(argv[0] if argv and not argv[0].startswith("--") else ".").resolve()

    def has_flag(flag: str) -> bool:
        return flag in argv

    compiled = compiler.compile_config(root, root / "web" / "config.toml", strip_asserts=has_flag("--no-asserts"))
    dist = compiler.write_dist(
        compiled,
        root / "dist" / "pyscript",
        extra_files={"web/config.toml": (root / "web" / "config.toml").read_text()},
    )
    raw = sum(len((root / rel).read_bytes()) for rel in compiled)
    size = sum(len(s.encode()) for s in compiled.values())
    print(f"compiled {len(compiled)} modules -> {dist}")
    print(f"raw {raw:,}B -> minified {size:,}B ({size / max(raw, 1):.0%})")
    if has_flag("--tar"):
        pin = releases.pinned(root)
        print(f"tarball: {compiler.tar_tree(dist, root / 'dist' / f'client-dist-{pin}.tar.gz')}")


if __name__ == "__main__":
    main()
