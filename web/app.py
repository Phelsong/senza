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
    await dom_router.routes.add(test_page, "/test")
    dom_router.routes()
    await dom_router.nav("/test")
    # ==================================


ensure_future(main())
