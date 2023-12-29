from pyscript import document
from pyweb.pydom import Element


class Button(Element):
    """Base component builder for an HTML button component.
    __Contains__
    id
    class
    inner_text
    """
    _type = "button"
    _class_list: set = {"button"}

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
        parent: Element
            The parent element to append the button to.
        id: str, optional
            The id of the button, by default ""
        class_list: set, optional
            A set of classes to apply to the button, by default {}
        inner_text: str, optional
            The inner text of the button, by default ""
        """
        self._parent: Element = parent
        self._js = document.createElement(self._type)
        self.id: str = id
        cl = self._class_list.union(class_list)
        self.html: str = f"{inner_text}"
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

    def add_class(self, class_name: str):
        """Add a class to the button.

        Parameters
        ----------
        class_name: str
            The class to add to the button.
        """
        self._js.classList.add(class_name)
        return self

    def remove_class(self, class_name: str):
        """Remove a class from the button.

        Parameters
        ----------
        class_name: str
            The class to remove from the button.
        """
        self._js.classList.remove(class_name)
        return self
