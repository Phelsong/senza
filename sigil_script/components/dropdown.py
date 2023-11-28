from pyscript import document
from pyweb.pydom import Element


class Dropdown(Element):
    """component builder for the card component."""

    _type = "select"
    _class_list: set[str] = {"uk-select", "dropdown"}

    def __opt_list__(self, item_list) -> str:
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
            value: str = "",
            item_list: dict[str, str] = {},
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
        self._js.value = value
        # -------------------
        li_list = self.__opt_list__(item_list)
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
