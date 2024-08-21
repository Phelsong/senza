"""base template"""

from senza.components import Rest, Element


class Label(Rest):
    """Base component builder for a HTML component.
    _type: str
    _class_list: set
    _parent: pydom.Element
    _js: pydom.Element
    id: str
    html: str
    """

    _type = "label"
    _class_list: set = {"label"}
