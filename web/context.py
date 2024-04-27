"""This file contains global site context variables"""

from pyweb.pydom import pydom
from senza.components.div import Div
from functools import lru_cache


@lru_cache
class Site:
    body: Div = Div(pydom["body"][0], id="root")


site = Site()
