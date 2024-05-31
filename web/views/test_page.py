from pyscript import when
from pyweb.pydom import Element
from senza.components import Div, Button
from senza.websocket import SWS


async def test_page(parent: Element):
    """test"""

    test_container = Div(parent, "test-div", inner_text="hello world")

    send_button = Button(test_container, "ws-button")
    url = "wss://local.dev:8062/ws"
    ws = SWS(url)

    @when("mousedown", send_button)
    async def ws_button(event):

        await ws.send_text("hello world")
        print(await ws.receive_text())
        # await ws.send_json({"hello": "world"})
        # await ws.send_bytes(b"hello world")
        # await ws.close()

    return test_container
