"""Div wrapper"""
from pyscript import document
from pyscript.web.elements import Element


class Div(Element):
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

        self._parent: Element = parent
        self._js = document.createElement(self._type)
        self.id: str = id
        self.visible = visible
        self.html = f"{inner_text}"
        # -------------------
        # create element
        # ---
        self.__create__(class_list)
        # ------------------
        # ------------------

        # -------------------------------------------------------------------------

    @property
    def visible(self) -> bool:
        """Get or set the visibility of the element."""
        return self._visible

    @visible.setter
    def visible(self, val: bool) -> bool:
        """Set the visibility of the element."""
        if val is True:
            self._js.style.visibility = "visible"
        else:
            self._js.style.visibility = "hidden"
        self._visible = val

    def __create__(self, class_list: set):
        self._parent.append(self)
        cl = self._class_list.union(class_list)
        for x in cl:
            self.add_class(x)
