#!pyscript
# libs
from asyncio import ensure_future

# imports
from senza.dom_router import dom_router
from web.context import site
from web.views.test_page import test_page


# =======================
async def main() -> None:
    # ==================================
    await dom_router.add(test_page)
    print(await dom_router.routes)
    await dom_router.nav("/test_page")
    # ==================================


ensure_future(main())
