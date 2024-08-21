from pyscript import document
from senza.components import Rest, Element


class Input(Rest):
    """component builder for the card component."""

    _type = "input"
    _class_list: set = {"input"}
