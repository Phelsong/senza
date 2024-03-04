"""P tag wrapper"""

from pyweb.pydom import Element
from senza.components import Rest


class P(Rest):
    _type = "p"
    _class_list: set = {"ptag"}
