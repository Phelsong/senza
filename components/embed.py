"""base template"""
from pyscript.web import Element
from senza.components.abase import Rest

class Embed(Rest):
    """Base component builder for a HTML component.
    _type: str
    _class_list: set
    _parent: pydom.Element
    _js: pydom.Element
    id: str
    html: str
    """

    _type = "embed"
    _class_list: set = {"embed"}
