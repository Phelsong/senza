"""router"""
# libs
from pyweb.pydom import Element

# imports
from sigil_script.context import site


class DomRouter:
    def __init__(self, root: Element) -> None:
        self.routes: dict = {}
        self.root: Element = root

    async def add_route(self, func: callable, route: str) -> None:
        self.routes[route] = func

    def remove_route(self, route: str) -> None:
        self.routes.__delitem__(route)

    def get_routes(self) -> set[str]:
        print(self.routes.keys())
        return self.routes.keys()

    async def nav(self, route: str) -> None:
        site.body.html = ""
        await dom_router.routes[route](self.root)


dom_router = DomRouter(site.body)
