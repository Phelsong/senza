from pyscript import document
from pyweb.pydom import Element
from senza.components import Rest


class SVG(Rest):
    """Base component builder for an HTML button component.
    __Contains__
    id
    class
    inner_text
    """

    _type = "div"
    _class_list: set = {"svg-container"}

    def __init__(
        self,
        parent: Element,
        id: str = "",
        *,
        class_list: set = {},
        svg_image: str = "",
    ):
        super().__init__(parent, id, class_list=class_list)
        self.html = f"{svg_image}"
