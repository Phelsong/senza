"""Div wrapper"""

from senza.components.abase import Rest

class Div(Rest):
    """Base component builder for an HTML button component.
    _type: str
    _class_list: set
    _parent: pydom.Element
    _js: pydom.Element
    id: str
    html: str
    """

    _type = "div"
    _class_list: set = {"container"}
