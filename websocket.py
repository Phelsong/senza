import js
import json

from asyncio import sleep
from typing import AsyncIterator
from functools import lru_cache


code = 1000
protocols = "protocols"
reason = "reason"


class SWS:

    CONNECTING = 0
    CONNECTED = 1
    DISCONNECTED = 2
    RESPONSE = 3

    def __init__(self, url: str):
        self._state = self.CONNECTING
        self._ws = js.WebSocket.new(url)
        self._messages: list[str | dict | bytes] = []
        self._ws.onmessage = self.on_message
        self._ws.onopen = self.on_open
        self._ws.onclose = self.on_close
        self._ws.onerror = self.on_error

    def __getattr__(self, attr):
        return getattr(self._ws, attr)

    # def __setattr__(self, attr, value):
    #     if attr == "onmessage":
    #         self._ws[attr] = lambda e: value(EventMessage(e))
    #     else:
    #         self._ws[attr] = value

    async def close(self, reason: str | None = None, code: int = 1000):
        self._ws.close(code, reason)

    async def receive(self, event, message) -> None:
        self._messages.append(message)

    # ------------------------------------

    @property
    @lru_cache(maxsize=1)
    def state(self):
        return self._state

    @state.setter
    def set_state(self, status: int):
        self._state = status

    # -------------------------------------

    async def on_open(self, event):
        try:
            print(event.type)
        except Exception as err:
            print(err)

    async def on_message(self, event):
        try:
            print("event: ", event.type, event.data)
            await self.receive(event.type, event.data)
        except Exception as err:
            print(err)

    async def on_close(self, event):
        try:
            print(event.type)
        except Exception as err:
            print(err)

    async def on_error(self, event):
        try:
            print(event.type)
        except Exception as err:
            print(err)

    # ------------------------------------

    async def send_text(self, text: str):
        try:
            if isinstance(text, str):
                self._ws.send(text)
            else:
                raise TypeError
        except TypeError as err:
            print(err)

    async def send_json(self, data: dict):
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
            await sleep(0.01)
            return await self.receive_text()
        try:
            assert type(self._messages[-1]) == str
        except AssertionError:
            return "type error"
        except IndexError as err:
            await sleep(0.01)
            return await self.receive_text()
        finally:
            return self._messages.pop()

    async def iter_text(self) -> AsyncIterator:
        try:
            while True:
                yield await self.receive_text()
        except Exception as err:
            print("iter_text: ", err)

    # ---

    async def receive_json(self) -> str:
        try:
            assert len(self._messages)
        except AssertionError:
            await sleep(0.01)
            return await self.receive_json()
        try:
            assert type(self._messages[-1]) == dict
        except AssertionError:
            return "type error"
        except IndexError as err:
            await sleep(0.01)
            return await self.receive_json()
        finally:
            return self._messages.pop()

    async def iter_json(self) -> AsyncIterator:
        try:
            while True:
                yield await self.receive_json()
        except Exception as err:
            print(err)

    # ---

    async def receive_bytes(self) -> str:
        try:
            assert len(self._messages)
        except AssertionError:
            await sleep(0.01)
            return await self.receive_bytes()
        try:
            assert type(self._messages[-1]) == bytes
        except AssertionError:
            return "type error"
        except IndexError as err:
            await sleep(0.01)
            return await self.receive_bytes()
        finally:
            return self._messages.pop()

    async def iter_bytes(self) -> AsyncIterator:
        try:
            while True:
                yield await self.receive_bytes()
        except Exception as err:
            print(err)
