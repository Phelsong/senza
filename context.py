"""This file contains global site context variables"""

from typing import Any
from pyscript import config, document
from pyscript.web import Element, page
from senza.components import Div


class Site:
    body: Div = Div(Element(document.body), "root")
    env: dict[str, Any] = {}
    base_url: str = config.get("fetch")[0]["from"]

    def add(self, element: Element) -> None:
        """adds element to the 'root' object, use for Bars/etc..."""
        self.body.append(element)


site = Site()
