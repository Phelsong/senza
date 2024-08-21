"""base template"""

from senza.components import Rest, Element


class Img(Rest):
    _type = "img"
    _class_list: set = {"img"}

    def __init__(
        self,
        parent: Element,
        id: str,
        *,
        class_list: set = set(),
        inner_text: str = "",
        visible: bool = True,
        src: str = "",
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

        EXTRA PARAMS
        -----------

        src: str
            html "src" attribute

        ===========

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
        super().__init__(
            parent, id, class_list=class_list, inner_text=inner_text, visible=visible
        )
        self.setAttribute("src", src)
