from pyscript import document
from pyscript.web.elements import Element


class Input(Element):
    """component builder for the card component."""

    _type = "input"
    _class_list: set = {"input"}

