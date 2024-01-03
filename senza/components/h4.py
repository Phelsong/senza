"""base template"""
from pyweb.pydom import Element


class H4(Element):
    """Base component builder for a HTML component.
    _type: str
    _class_list: set
    _parent: pydom.Element
    _js: pydom.Element
    id: str
    html: str
    """

    _type = "h4"
    _class_list: set = {"h4"}
