#!pyscript
# libs
from asyncio import ensure_future

# imports
from sigil_script.dom_router import dom_router
from web.views.test_page import test_page


# =======================
async def main() -> None:
    # ==================================
    await dom_router.add_route(test_page, "/test")
    dom_router.get_routes()
    await dom_router.nav("/test")
    # ==================================


ensure_future(main())
