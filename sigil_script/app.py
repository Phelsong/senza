#!pyscript
# libs
from asyncio import ensure_future

from pyscript import when

# imports
from context import site
from elements.navbar import navbar
from views.edit import edit
from views.gallery_view import generate_gallery_view


# =======================
async def main() -> None:
    # ==================================
    # injected variables
    site.callback_url = callback_url

    # =================================

    await navbar(site.body)
    await generate_gallery_view("Football", site.gallery)

    # ====================================a=================================
    @when("click", selector="#sidebar-list")
    async def bar_button_handler(event) -> None:
        event.preventDefault()
        await generate_gallery_view(event.target.id.strip("#"), site.gallery)
    # ====================================b=================================


if route == "edit":
    ensure_future(edit())
else:
    ensure_future(main())
