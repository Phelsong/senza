"""base template"""
from pyscript.web import Element
from senza.components.abase import Rest

class canvas(Rest):
    """Base component builder for a HTML component.
    _type: str
    _class_list: set
    _parent: pydom.Element
    _js: pydom.Element
    id: str
    html: str
    """

    _type = "canvas"
    _class_list: set = {"canvas"}
