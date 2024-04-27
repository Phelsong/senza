"""router"""

# from typing_extensions import dict_keys
from typing import Callable

# libs
from pyweb.pydom import Element

# imports
from web.context import site


class DomRouter:
    async def __init__(self, root: Element) -> None:
        self._nav: dict[str, Callable] = {}
        self.root: Element = root
        self.routes: set[str] = set()

    async def remove_route(self, route: str) -> None:
        self.routes.remove(route)
        del self.routes[route]

    @property
    async def routes(self) -> set[str]:
        return self.routes

    @routes.setter
    async def routes(self, func: Callable, route: str) -> None:
        self.routes.add(route)
        self.routes[route] = func

    @routes.deleter
    async def routes(self, route: str) -> None:
        self.routes.remove(route)
        del self.nav[route]

    async def nav(self, route: str) -> None:
        site.body.html = ""
        await dom_router.nav[route](self.root)


dom_router = DomRouter(site.body)
