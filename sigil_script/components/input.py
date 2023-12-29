from pyscript import document
from pyweb.pydom import Element


class Input(Element):
    """component builder for the card component."""

    _type = "input"
    _class_list: set = {"input"}

