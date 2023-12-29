from pyscript import document
from pyweb.pydom import Element


class Form(Element):
    """component builder for the form component."""

    _type = "form"
    _class_list: set = {"form"}
