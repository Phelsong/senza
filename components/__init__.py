# from asyncio import ensure_future
# from pyscript import py_import

# (abase, div, anchor, button, form, img, input, label, h1, h2, h3, h4, h5, h6, ptag,
#  svg, span) = await py_import(
# 	"senza.components.abase, senza.components.div, "
#                               " senza.components.anchor, senza.components.button, "
#                               " senza.components.form, senza.components.img, "
#                               " senza.components.input, senza.components.label, "
#                               " senza.components.h1, senza.components.h2, "
#                               " senza.components.h3, senza.components.h4, "
#                               " senza.components.h5, senza.components.h6, "
#                               " senza.components.ptag, senza.components.svg, "
#                               " senza.components.span ")

# div = ensure_future(py_import("senza/components/div.py"))
# img = ensure_future(py_import("senza/components/img.py"))
# SVG = ensure_future(py_import("senza/components/svg.py"))
# P = ensure_future(py_import("senza/components/ptag.py"))

##
from senza.components.abase import Rest
from senza.components.div import Div
from senza.components.anchor import A
from senza.components.button import Button

from senza.components.form import Form
from senza.components.img import Img
from senza.components.input import Input
from senza.components.label import Label
from senza.components.h1 import H1
from senza.components.h2 import H2
from senza.components.h3 import H3
from senza.components.h4 import H4
from senza.components.h5 import H5
from senza.components.h6 import H6

# from senza.components.option import Option
# from senza.components.pre import Pre
# from senza.components.embed import Embed
from senza.components.ptag import P

from senza.components.select import Select
from senza.components.svg import SVG

# from senza.components.small import Small
from senza.components.span import Span

# from senza.components.code import Code
# from senza.components.strong import Strong
# from senza.components.sub import Sub

# from senza.components.table import Table
# from senza.components.tr import Tr
