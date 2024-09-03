"""base template"""

from pyscript.web import Element
from senza.components.abase import Rest


class A(Rest):
    """Base component builder for a HTML component.
    _type: str
    _class_list: set
    _parent: pydom.Element
    _js: pydom.Element
    id: str
    html: str
    """

    _type = "a"
    _class_list: set = {"a"}

    def __init__(
        self,
        parent: Element,
        id: str = "",
        *,
        class_list: set = set(),
        href: str = "",
        inner_text: str = "",
        inner_html: str = ""
    ):
        super().__init__(
            parent,
            id,
            class_list=class_list,
            inner_text=inner_text,
        )
        self.__setattr__("innerHTML", inner_html)
        self.__setattr__("href", href)
