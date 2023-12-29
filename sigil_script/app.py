#!pyscript
# libs
from asyncio import ensure_future

from pyscript import when

# imports
from sigil_script.components.div import Div
from sigil_script.components.button import Button
from sigil_script.context import site


# =======================
async def main() -> None:
    # ==================================
    div1 = Div(site.body, inner_text="hello")
    but1 = Button(site.body, inner_text="world")
    
    # ==================================


ensure_future(main())
