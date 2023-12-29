"""This file contains global site context variables"""
from pyweb import pydom
from sigil_script.components.div import Div


class Site:
    body: Div = Div(pydom["body"][0], id="main")


site = Site()
