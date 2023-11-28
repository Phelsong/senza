from pyscript import document
from pyweb.pydom import Element


class Title(Element):
    """component builder for the card component."""

    _type = "h3"
    _class_list: set = {"title"}

    def __init__(
            self,
            parent: Element,
            id: str = "",
            *,
            class_list: set = {},
            inner_text: str = "",
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
        self.inner_text = inner_text
        self.html = f"<span>{inner_text}</span>"
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
        self._js.value = self.inner_text

    # -------------------------------------------------------------------------

    def __create__(self):
        self._parent.append(self)
