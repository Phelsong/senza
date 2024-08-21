from pyscript import document
from senza.components.abase import Rest, Element


class Select(Element):
    """component builder for the card component."""

    _type = "select"
    _class_list: set[str] = {"uk-select", "dropdown"}

    def __opt_list__(self, opt_list: dict, opt_class: set) -> str:
        opt_list = ""
        opt_class = opt_class.add("select-item")
        for id, val in self.opt_list.items():
            opt_list += f"<option class={opt_class} id={id} value={val}></option>"
        return opt_list

    def __init__(
        self,
        parent: Element,
        id: str = "",
        *,
        class_list: set = {},
        default_value: str = "",
        opt_list: dict[str, str] = {},
        opt_class: set = {},
    ):
        """
        Parameters
        ----------
        id
        class_list
        """
        self._parent: Element = parent
        self._js = document.createElement(self._type)
        self.id = id
        cl = self._class_list.union(class_list)
        self._js.value = default_value
        # -------------------
        li_list = self.__opt_list__(opt_list, opt_class)
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
