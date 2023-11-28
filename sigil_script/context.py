"""This file contains global site context variables"""
from pyweb import pydom
from components.div import Div


class Site:
    body: Div = Div(pydom["body"][0], id="main")
    gallery: Div = Div(body, id="gallery-container")
    form: Div = Div(body, id="edit-form-container", visible=False)
    callback_url: str


site = Site()

submit_query: dict[str, str] = {
    "cartId": "",
    "designNumber": "",
    "currentLocation": "",
    "redirectUrl": "",
    "callbackUrl": "",
    "text1": "",
    "text2": "",
    "text3": "",
    "text4": "",
    "color1": "",
    "color2": "",
    "color3": "",
    "color4": "",
    "currentLocation": "",
    "specialInstructions": "",
    "reversedOut": "",
}
