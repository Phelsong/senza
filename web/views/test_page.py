from pyweb.pydom import Element
from senza.components import Div


async def test_page(parent: Element):
    """test"""

    test_container = Div(parent, inner_text="hello world")
    return test_container
