"""base template"""

from senza.components.abase import Rest, Element


class Iframe(Rest):

    _type = "iframe"
    _class_list: set = {"iframe"}
