from pyscript import display, document, window
from pyweb import pydom
from pyweb.pydom import Element


class Dropdown(Element):
    """component builder for the card component."""

    _type = "select"
    _class_list: set[str] = {"uk-select", "dropdown"}
    color_list: dict[str] = {"test": "blue"}

    def __color_list__(self) -> str:
        opt_list = ""
        for id, color in self.color_list.items():
            opt_list += f"<option class=color-swatch id={id} value={color}></option>"
        return opt_list

    def __init__(
        self,
        parent: Element,
        id: str = "",
        *,
        class_list: set = {},
        inner_text: str = "",
        value:str = "",
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
        self.value = value
        # -------------------
        li_list = self.__color_list__()
        self.html = f"""
        {li_list}
        """
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

    def __create__(self):
        self._parent.append(self)

