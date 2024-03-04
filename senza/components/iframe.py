"""base template"""
from pyweb.pydom import Element


class Iframe(Element):


    _type = "iframe"
    _class_list: set = {"iframe"}
