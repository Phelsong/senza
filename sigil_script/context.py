"""This file contains global site context variables"""
from stubs.pyweb import pydom
from components.div import Div


class Site:
    body: Div = Div(pydom["body"][0], id="main")



site = Site()
