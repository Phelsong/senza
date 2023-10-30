#!pyscript
# libs
from pyscript import when
from pyweb import pydom
from pyweb.pydom import BaseElement, Element
from pyodide.http import pyfetch
from asyncio import ensure_future

# imports


base_url: str = "http://[::1]:8001"


# =======================
async def main() -> None:
    from card import Card
    from button import Button
    from svg import SVG
    from div import Div
    from side_bar import SideBar
    from queries import get_svg_list, get_svg, query_ex, get_folder

    # ============
    #   print("jsessonid", jsessionid)

    # ==================================

    main_body: Element = pydom.create("div")
    main_body.id: str = "main"
    pydom["body"][0].append(main_body)

    # =================================
    side_bar: SideBar = SideBar(main_body, id="side-bar")

    bar_button: Div = Div(
        main_body,
        id="bar-button-container",
        inner_text="""<button
        id='bar-button'
        class='uk-button'
        uk-toggle='target: #offcanvas-reveal'
        type='button'
        ><svg id="bar-button" stroke="currentColor" fill="none" stroke-width="0" viewBox="0 0 15 15" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M1.5 3C1.22386 3 1 3.22386 1 3.5C1 3.77614 1.22386 4 1.5 4H13.5C13.7761 4 14 3.77614 14 3.5C14 3.22386 13.7761 3 13.5 3H1.5ZM1 7.5C1 7.22386 1.22386 7 1.5 7H13.5C13.7761 7 14 7.22386 14 7.5C14 7.77614 13.7761 8 13.5 8H1.5C1.22386 8 1 7.77614 1 7.5ZM1 11.5C1 11.2239 1.22386 11 1.5 11H13.5C13.7761 11 14 11.2239 14 11.5C14 11.7761 13.7761 12 13.5 12H1.5C1.22386 12 1 11.7761 1 11.5Z" fill="currentColor"></path></svg>
        </button>""",
    )

    # =====================================================================
    gallery_container: Div = Div(main_body, id="gallery-container")


    async def generate_gallery_view(files: dict[str]):
        gallery_container.html = ""
        print(files)
        for key, val in files.items():
            card_container: Div = Div(
                gallery_container,
                id=f"card-container-{key}",
                class_list={"card-container"},
            )

            card: Card = Card(card_container, id=f"c-{key}")

            SVG(
                card,
                f"z{key}",
                svg_image=val,
            )

            Button(
                card,
                f"s@{key}",
                class_list={"gallery-button"},
                inner_text="select",
            )

            @when("click", selector=".gallery-button")
            async def svg_handler(event) -> None:
                event.stopPropagation()
                id = event.target.id.strip("s@")

                svg = pydom[f"#z{id}"]

                from input_form import form_page

                main_body.html = ""
                await form_page(id, svg)

    @when("click", selector=".gallery-button")
    async def svg_handler(event) -> None:
        event.stopPropagation()
        id = event.target.id.strip("s@")

        svg = pydom[f"#z{id}"]

        from input_form import form_page

        main_body.html = ""
        await form_page(id, svg)

    @when("click", selector="#sidebar-list")
    async def bar_button_handler(event) -> None:
        event.preventDefault()
        print(event.target.id)
        files = await get_folder(event.target.id.strip("#"))
        await generate_gallery_view(files)

    # =====================================================================


ensure_future(main())


# =======================
