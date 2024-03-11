"""base template"""
from pyweb.pydom import Element
from senza.components.abase import Rest

class Iframe(Rest):


    _type = "iframe"
    _class_list: set = {"iframe"}
