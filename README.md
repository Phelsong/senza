# Senza

A thin layer of conveniences on top of **pyScript** (2025.11+ / 2026.x),
with as little re-invention of pyScript as possible.

Three modules + dev utils:

- `config.py` — pyscript app config utilities: modern `[files]` map sync
  (`sync_files`), legacy `[[fetch]]` migration, the senza `{SENZA}`
  placeholder (browser modules served from `<app-root>/packages/senza`,
  populated by `senza/sync_senza.py`), TOML dump with round-trip
  verification, and the pyodide `interpreter` pin (`pyodide.version` at the app root)
- `router.py` — a client-side DOM router built on `pyscript.web` + the history API:
  - `router.add(view, "/path")` or `@router.route("/path")` — a view is a plain
    (optionally async) function returning a `pyscript.web` element
  - `await router.navigate("/path")` — swaps the router root's content, pushes history
  - back/forward buttons work automatically (`popstate`)
  - `router.link(text, "/path")` — a SPA-aware `<a>`
  - `router.not_found = view` for 404s
- `visibility.py` — quick element hiding without wrapper classes:
  `hide / show / toggle / is_hidden`; self-installs the
  `.senza-hidden { display: none !important }` rule on first use
- `releases.py` — framework-agnostic pyScript release pinning (library + CLI),
  usable from any server that embeds pyScript. State:
  - `<app-root>/pyscript.version` — the pin the app's shell reads
  - `releases.txt` next to this file — pin history, appended on change

  ```python
  from senza.releases import pinned, check, pin

  pinned("/path/to/app")         # "2026.7.3"
  check("/path/to/app")          # compare against upstream tags
  pin("latest", "/path/to/app")  # bump + log
  ```

  CLI: `python senza/releases.py {check|latest|pin <version>} [--root <app>]` —
  the app root is auto-discovered by scanning upward for `pyscript.version`,
  so running it inside an app checkout needs no flags.

- `scripts/` — all senza management/dev scripts (run from any app root):
  `sync_senza.py` (packages copy refresh + config migration),
  `sync_web_config.py` (`[files]` map sync), `compile_dist.py` (minified dist),
  `compile_sass.py`, `sync_pyodide.py` (pyodide pin/download + config
  `interpreter` key), `sync_pyscript_lsp.py` (pyScript stdlib for LSP + root
  symlinks + pyrightconfig). Library modules stay at the senza root.

Server frameworks provide the wrapper layer themselves (e.g. the outer
`senza-fastapi` repo binds these functions to its project root and renders its
own shell HTML).

## What was removed

`components/*` (per-tag wrapper classes), `context.py` (`Site`), the vendored
`pyscript/` stdlib copies, `dom_router.py`, and `websocket.py` (`SenzaSocket`)
— all are now first-class in pyScript itself:

| old senza piece        | use pyScript instead                          |
|------------------------|-----------------------------------------------|
| `Div`, `Button`, `H1`… | `from pyscript import web` → `web.div(...)`, `web.button(...)` |
| `Rest` (`abase.py`)    | `web.div(children, id=..., classes=[...], style={...})` |
| `Site` / `context`     | `web.page`, `web.page.body`, `web.page["my-id"]` |
| `dom_router`           | `senza.router`                                |
| `SenzaSocket`          | `from pyscript import WebSocket`              |

## Usage sketch

```python
from pyscript import web
from senza.router import Router

content = web.main(id="main")
web.page.append(content)
app_router = Router(root=content)

@app_router.route("/about")
def about():
    return web.div(web.h1("About"))
```