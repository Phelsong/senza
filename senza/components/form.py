from pyscript import document
from pyweb.pydom import Element
from senza.components.abase import Rest

class Form(Rest):
    """component builder for the form component."""

    _type = "form"
    _class_list: set = {"form"}
