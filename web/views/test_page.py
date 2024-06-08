from pyscript import when
from pyweb.pydom import Element
from senza.components import Div, Button
from senza.websocket import SWS


async def test_page(parent: Element):
    """test"""

    test_container = Div(parent, "test-div", inner_text="hello world")

    send_button = Button(test_container, "ws-button")
    stop_button = Button(test_container, "ws-stop-button")

    url = "wss://local.dev:8062/ws"
    ws = SWS(url)

    # @when("mousedown", send_button)
    # async def button_receive_text(event):
    #     await ws.send_text(f"hello world x{x}")
    #     print(await ws.receive_text())

    # @when("mousedown", send_button)
    # async def button_iter_text(event):

    #     for x in range(10):
    #         await ws.send_text(f"hello world x{x}")
    #     async for y in ws.iter_text():
    #         print(y)

    # @when("mousedown", send_button)
    # async def button_receive_json(event):
    #     await ws.send_json({"hello": "world"})
    #     print(await ws.receive_json())

    # @when("mousedown", send_button)
    # async def button_iter_json(event):

    #     for x in range(10):
    #         await ws.send_json({"hello_world": f"{x}"})
    #     async for y in ws.iter_json():
    #         print(y)

    # @when("mousedown", send_button)
    # async def button_receive_bytes(event):
    #     await ws.send_bytes(b"hello world")
    #     print(str(await ws.receive_bytes()))

    @when("mousedown", send_button)
    async def button_iter_bytes(event):

        for x in range(10):
            await ws.send_bytes(b"hello world")
        async for y in ws.iter_bytes():
            print(str(y))

    @when("mousedown", stop_button)
    async def stop_button(event):
        await ws.close()

    return test_container
