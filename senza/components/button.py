"""base template"""
from pyweb.pydom import Element
from senza.components.abase import Sigil


class Button(Sigil):
    """Base component builder for a HTML component.
    _type: str
    _class_list: set
    _parent: pydom.Element
    _js: pydom.Element
    id: str
    html: str
    """

    _type = "button"
    _class_list: set = {"button"}
