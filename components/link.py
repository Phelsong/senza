"""base template"""

from senza.components import Rest, Element


class Link(Element):
    """Base component builder for a HTML component.
    _type: str
    _class_list: set
    _parent: pydom.Element
    _js: pydom.Element
    id: str
    html: str
    """

    _type = "link"
    _class_list: set = {"link"}
