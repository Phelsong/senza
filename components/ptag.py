"""P tag wrapper"""

from pyscript.web.elements import Element
from senza.components import Rest


class P(Rest):
    _type = "p"
    _class_list: set = {"ptag"}
