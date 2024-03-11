"""base template"""

from pyweb.pydom import Element
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
