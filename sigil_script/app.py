#!pyscript
# libs
from asyncio import ensure_future

from pyscript import when

# imports
from components.div import Div
from context import site


# =======================
async def main() -> None:
    # ==================================
    div1 = Div(site.body)

    # ==================================


ensure_future(main())
