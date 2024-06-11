"""base template"""
from pyscript.web.elements import Element
from senza.components.abase import Rest

class H5(Rest):
    """Base component builder for a HTML component.
    _type: str
    _class_list: set
    _parent: pydom.Element
    _js: pydom.Element
    id: str
    html: str
    """

    _type = "h5"
    _class_list: set = {"h5"}
