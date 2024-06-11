"""This file contains global site context variables"""

from pyscript.web import dom
from senza.components.div import Div


class Site:
    body: Div = Div(dom["body"][0], id="root")


site = Site()
