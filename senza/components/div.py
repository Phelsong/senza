"""Div wrapper"""
from pyscript import document
from pyweb.pydom import Element
from senza.components.abase import Rest

class Div(Rest):
    """Base component builder for an HTML button component.
    _type: str
    _class_list: set
    _parent: pydom.Element
    _js: pydom.Element
    id: str
    html: str
    """

    _type = "div"
    _class_list: set = {"container"}

    def __init__(
        self,
        parent: Element,
        id: str = "",
        *,
        class_list: set = {},
        inner_text: str = "",
        visible: bool = True,
    ):
        """
        Parameters
        ----------
        parent: Element
            The parent element to append the component to.
        id: str
            The id of the component.
        class_list: set
            A set of classes to apply to the component.
        inner_text: str
            The inner text of the component.
        visible: bool
            Whether the component is visible or not.
        """
