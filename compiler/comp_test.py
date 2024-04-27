"""base template"""

# from stubs.pyscript import document
# from stubs.pyweb.pydom import Element
from pyscript import document
from pyweb import pydom
from pyweb.pydom import Element


class Rest(Element):
    """Base component builder for a HTML component.
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
        id: str,
        *,
        class_list: set = set(),
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

        Methods
        -------
        html: str
        id: str
        value: str
        children: str
        visible: bool
        add_class: str
        remove_class: str
        classes
        clone(id: str)
        show_me
        content
        when
        """

        self._parent: Element = parent
        self._js = document.createElement(self._type)
        self.id = id
        self.html = f"{inner_text}"
        # -------------------
        # create element
        # ---
        self.__create__(class_list)
        # after create
        self.visible = visible
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
            pydom[f"#{self.id}"][0].remove_class("senza-hidden")
        else:
            pydom[f"#{self.id}"][0].add_class("senza-hidden")
        self._visible = val

    def __create__(self, class_list: set):
        self._parent.append(self)
        cl = self._class_list.union(class_list)
        for x in cl:
            self.add_class(x)
