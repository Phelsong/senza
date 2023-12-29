from pyscript import document
from pyweb.pydom import Element


class Input(Element):
    """component builder for the card component."""

    _type = "input"
    _class_list: set = {"input"}

    def __init__(
        self,
        parent: Element,
        id: str = "",
        *,
        class_list: set = {},
        inner_text: str = "",
    ):
        """
        Create an input component.

        Parameters
        ----------
        parent : Element
            the parent element of the input component
        id : str, optional
            the id of the input component, by default ""
        class_list : set, optional
            a set of classes to be added to the input component, by default {}
        inner_text : str, optional
            the inner text of the input component, by default ""
        """
        self._parent: Element = parent
        self._js = document.createElement(self._type)
        self.id = id

        self.html = f"{inner_text}"
        # -------------------
        # create element
        # ---
        self.__create__()
        # ------------------

    # -------------------------------------------------------------------------

    def __create__(self):
        self._parent.append(self)
        cl = self._class_list.union(class_list)
        for x in cl:
            self.add_class(x)
