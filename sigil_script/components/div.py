from pyscript import document
from pyweb.pydom import Element


# from out import pydom
# from out.pydom import Element


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
    _class_list: set = {"uk-container", "container"}

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
        id
        class_list
        """
        self._parent: Element = parent
        self._js = document.createElement(self._type)
        self.id: str = id
        cl = self._class_list.union(class_list)
        self.html = f"{inner_text}"
        self.visible = visible
        # -------------------
        # create element
        # ---
        self.__create__()
        # ------------------
        # must be after creation of element
        # ---
        for x in cl:
            self.add_class(x)

        # ------------------

    # -------------------------------------------------------------------------
    @property
    def visible(self) -> bool:
        return self._visible

    @visible.setter
    def visible(self, val:bool) -> bool:
        if val is True:
            self._js.style.visibility = "visible"
        else:
            self._js.style.visibility = "hidden"
        self._visible = val

    def __create__(self):
        self._parent.append(self)
