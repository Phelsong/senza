"""Client-side DOM router for pyscript apps.

Built directly on `pyscript.web` element classes and the browser history API.
Provides:

- declarative route registration: `router.add(view, "/path")` or `@router.route("/path")`
- SPA navigation: `router.navigate("/path")` swaps the router root's content
- back/forward support via `popstate`
- `router.link()` creates SPA-aware anchor elements

A shared default instance `router` (rooted at `page.body`) is provided, but you
will usually construct your own instance rooted at a layout container (see
`web/app.py`). A view is a function that returns the `pyscript.web` element to
display, or `None` if it has already rendered itself.

Note on events: pyscript's `Event.trigger` invokes listeners synchronously and
discards coroutine objects, so async listener functions would never run — click
handlers here are therefore sync wrappers over `asyncio.ensure_future`.
"""

import asyncio
from inspect import isawaitable
from typing import Any, Callable, Optional, Union

from pyscript import web, window
from pyscript.ffi import create_proxy, to_js

View = Callable[[], Any]
ViewResult = Union[web.Element, web.ElementCollection, str, None]


def _normalize(path: str) -> str:
    """Reduce a path or absolute same-origin URL to `/foo` form."""
    path = (path or "/").strip()
    if "://" in path:  # absolute URL (e.g. `link.href`) -> strip the origin
        origin = f"{window.location.protocol}//{window.location.host}"
        path = path[len(origin):] if path.startswith(origin) else "/" + path.split("/", 3)[-1]
    if not path.startswith("/"):
        path = f"/{path}"
    if len(path) > 1:
        path = path.rstrip("/")
    return path or "/"


class Router:
    def __init__(self, root: Optional[web.Element] = None) -> None:
        self.root: web.Element = root if root is not None else web.page.body
        self._views: dict[str, View] = {}
        self.not_found: Optional[View] = None
        self._current_path: str = ""
        # support browser back/forward buttons
        window.addEventListener("popstate", create_proxy(self._on_popstate))

    # ------------------------------------------------------------- registry

    @property
    def routes(self) -> tuple[str, ...]:
        return tuple(self._views)

    def route(self, path: str) -> Callable[[View], View]:
        """Decorator form of `add`: `@router.route("/about")`."""

        def decorator(view: View) -> View:
            self.add(view, path)
            return view

        return decorator

    def add(self, view: View, path: str) -> None:
        """Register `view` at `path`. Re-registering a path replaces its view."""
        self._views[_normalize(path)] = view

    def remove(self, path: str) -> None:
        self._views.pop(_normalize(path), None)

    # ------------------------------------------------------------ rendering

    async def navigate(self, path: str, push: bool = True) -> None:
        """Render the view registered at `path` into `self.root`.

        A view that raises renders the traceback into the router root (and
        logs to the console) instead of leaving a mysteriously blank page.
        """
        path = _normalize(path)
        if path == self._current_path:
            return
        view = self._views.get(path)
        if view is None:
            view = self.not_found
            if view is None:
                return  # nothing registered and no not_found view: leave the DOM alone
        self._current_path = path
        if push:
            # state must be a JS value: a Python dict isn't implicitly clonable
            window.history.pushState(to_js({}), "", path)
        self.root.innerHTML = ""
        try:
            result = view()
            if isawaitable(result):
                result = await result
        except Exception as err:  # noqa: BLE001 - the router IS the error boundary
            window.console.error(f"[senza.router] view {path} failed: {err!r}")
            self.root.append(
                web.pre(
                    f"route {path} failed: {err!r}",
                    classes=["route-error"],
                    style={
                        "color": "firebrick",
                        "white-space": "pre-wrap",
                        "font-family": "monospace",
                        "padding": "1rem",
                        "border": "1px solid firebrick",
                    },
                )
            )
            return
        if result is not None:
            self.root.append(result)

    def _on_popstate(self, event: Any) -> None:
        path = window.location.pathname
        self._current_path = ""  # force a render even if returning to same path
        if path in self._views or self.not_found is not None:
            asyncio.ensure_future(self.navigate(path, push=False))

    # -------------------------------------------------------------- helpers

    def link(
        self,
        text: str,
        path: str,
        classes: Union[list[str], set[str], None] = None,
    ) -> web.a:
        """Create a SPA-aware `<a>`; navigates client-side without a reload."""
        target = _normalize(path)
        link = web.a(text, href=target)

        def click_link(event: Any) -> None:
            # stop the browser's default navigation BEFORE anything async
            event.preventDefault()
            try:
                asyncio.ensure_future(self.navigate(target))
            except Exception as err:  # noqa: BLE001
                window.console.error(f"[senza.router] could not navigate {target}: {err!r}")
                self.root.append(web.pre(f"navigation failed: {err!r}", classes=["route-error"]))

        link.on_click = click_link
        return link


def router_factory(root: Optional[web.Element] = None) -> Router:
    """Create a new Router. Apps should have exactly ONE instance — pass it to
    layout helpers so their links bind to it (creating a second instance
    silently produces links that navigate nowhere)."""
    return Router(root)