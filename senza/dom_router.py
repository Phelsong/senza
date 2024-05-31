"""router"""

# from typing_extensions import dict_keys
from typing import Callable

# libs
from pyweb.pydom import Element

# imports
from web.context import site


class DomRouter:
    def __init__(self, root: Element) -> None:
        self.root: Element = root
        self._nav: dict[str, Callable] = {}
        self._routes: set[str] = set()

    @property
    async def routes(self) -> set[str]:
        return self._routes

    async def add(self, func: Callable, route: str = "{/func.__name__}") -> None:
        #
        if route == "{/func.__name__}":
            route = f"/{func.__name__}"
        if route[0] != "/":
            route = f"/{route}"
        #
        self._routes.add(route)
        self._nav[f"/{func.__name__}"] = func

    async def remove(self, route: str) -> None:
        self._routes.remove(route)
        del self._nav[route]

    async def nav(self, route: str) -> None:
        site.body.html = ""
        await self._nav[route](self.root)


dom_router = DomRouter(site.body)
