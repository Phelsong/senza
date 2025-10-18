"""Div wrapper"""

from senza.components.abase import Rest, Element


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
        id: str,
        *,
        class_list: set = set(),
        inner_text: str = "",
        inner_html: str = "",
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
        super().__init__()

        self.parent: Element = parent
        self.id = id
        self.innerHtml = f"{inner_html}"
        self.innerText = inner_text
        # -------------------
        # create element
        # ---
        self.__create__(parent, class_list)
        # after create
        self.visible    def __init__(
             self,
             parent: Element,
             id: str = "",
             *,= visible
