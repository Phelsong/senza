"""Div wrapper"""

from pyscript import document
from pyweb.pydom import Element
from senza.components.abase import Rest


class Div(Rest):
    _type = "div"
    _class_list: set = {"container"}
