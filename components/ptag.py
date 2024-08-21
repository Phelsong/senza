"""P tag wrapper"""

from senza.components import Rest, Element


class P(Rest):
    _type = "p"
    _class_list: set = {"ptag"}
