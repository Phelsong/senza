"""base template"""

from senza.components.abase import Rest, Element


class Span(Rest):
    """Base component builder for a HTML component.
    _type: str
    _class_list: set
    _parent: pydom.Element
    _js: pydom.Element
    id: str
    html: str
    """

    _type = "span"
    _class_list: set = {"span"}
