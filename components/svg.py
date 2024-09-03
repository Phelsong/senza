from pyscript import document
from senza.components import Rest, Element


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
        class_list: set = set(),
        svg_image: str = "",
    ):
        super().__init__(parent, id, class_list=class_list)
        self.innerHTML = f"{svg_image}"
