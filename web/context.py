"""This file contains global site context variables"""
from pyweb import pydom
from senza.components.div import Div


class Site:
    body: Div = Div(pydom["body"][0], id="root")


site = Site()
