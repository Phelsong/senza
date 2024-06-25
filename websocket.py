import js
import json
import orjson

from asyncio import sleep
from typing import AsyncIterator, Callable, Union, Any
from functools import lru_cache




# code = 1000
# protocols = "protocols"
# reason = "reason"


class SenzaSocket:
    CONNECTING: int = 0
    CONNECTED: int = 1
    CLOSING: int = 2
    CLOSED: int = 3

    def __init__(self, url: str):
        self._state = self.CONNECTING
        self._ws = js.WebSocket.new(url)
        self._messages: list[str | dict | bytes] = []
        self._ws.onmessage = self.on_message
        self._ws.onopen = self.on_open
        self._ws.onclose = self.on_close
        self._ws.onerror = self.on_error

    async def aconnect(self):
        try:
            assert self._ws.readyState == self.CONNECTED
            self.state = self.CONNECTED
            return True
        except AssertionError:
            await sleep(0.001)
            await self.aconnect()


    async def close(self, code: int = 1000, reason: str | None = None) -> None:
        self._ws.close(code, reason)
        self.state = self.CLOSING

    async def receive(self, event, message) -> None:
        self._messages.append(message)

    # ------------------------------------

    @property
    def state(self) -> int:
        return self._state

    @state.setter
    def state(self, status: int) -> None:
        self._state = status

    # -------------------------------------

    async def on_open(self, event) -> None:
        try:
            print(event.type)
            self.state = self.CONNECTED
        except Exception as err:
            print(err)

    async def on_message(self, event) -> None:
        try:
            await self.receive(event.type, event.data)
        except Exception as err:
            print(err)

    async def on_close(self, event) -> None:
        try:
            print(event.type)
        except Exception as err:
            print(err)

    async def on_error(self, event) -> None:
        try:
            print(event.type)
        except Exception as err:
            print(err)

    # ------------------------------------

    async def send_text(self, text: str) -> None:
        try:
            if isinstance(text, str):
                self._ws.send(text)
            else:
                raise TypeError
        except TypeError as err:
            print(err)

    async def send_json(self, data: dict) -> None:
        try:
            if isinstance(data, dict):
                self._ws.send(json.dumps(data))
            else:
                raise TypeError
        except TypeError as err:
            print(err)

    async def send_bytes(self, data):
        try:
            buffer = js.Uint8Array.new(len(data))
            for pos, b in enumerate(data):
                buffer[pos] = b
            self._ws.send(buffer)
        except Exception as err:
            print(err)

    # ------------------------------------

    async def receive_text(self) -> str:
        try:
            assert len(self._messages)
        except AssertionError:
            await sleep(0.05)
            return await self.receive_text()
        try:
            assert type(self._messages[-1]) is str
            return self._messages.pop()
        except AssertionError:
            return "type error"
        except IndexError as err:
            await sleep(0.05)
            return await self.receive_text()


    async def iter_text(self) -> AsyncIterator[str]:
        try:
            while True:
                yield await self.receive_text()
        except Exception as err:
            print("iter_text: ", err)

    # ----------------------------------

    async def receive_json(self) -> list[Any] | dict[Any, Any] | None:
        try:
            assert len(self._messages)
        except AssertionError:
            await sleep(0.05)
            return await self.receive_json()
        try:
            mess = orjson.loads(self._messages[-1])
            assert type(mess) is dict or type(mess) is list
            self._messages.pop()
            return mess
        except AssertionError:
            print(f"type error {type(self._messages[-1])}")
        except IndexError as err:
            await sleep(0.05)
            return await self.receive_json()
        except Exception as err:
            print(err)


    async def iter_json(self) -> AsyncIterator[dict[Any, Any] | list[dict[Any, Any]]]:
        try:
            while True:
                yield await self.receive_json()
        except Exception as err:
            print(err)

    # ---

    async def receive_bytes(self) -> bytes | None:
        try:
            assert len(self._messages)
        except AssertionError:
            await sleep(0.05)
            await self.receive_bytes()
        try:
            # assert type(self._messages[-1]) == object
            return self._messages.pop()
        except AssertionError:
            print("assert error", str(self._messages[-1]))
            print(f"type error, receive is {type(self._messages[-1])}")
        except IndexError as err:
            await sleep(0.05)
            await self.receive_bytes()

    async def iter_bytes(self) -> AsyncIterator:
        try:
            while True:
                yield await self.receive_bytes()
        except Exception as err:
            print("iter ", err)
