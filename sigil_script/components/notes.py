from pyscript import document
from pyweb.pydom import Element


class Notes(Element):
    """component builder for the card component."""

    _type = "div"
    _class_list: set[str] = {"notes"}

    def __init__(
            self,
            parent: Element,
            id: str = "",
            title: str = "",
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
        self.html = f"""
        <ul uk-accordion class="accordian">
        <li class="uk-open accordian-item">
        <a class="uk-accordion-title" href="#">{title}</a>
        <div class="uk-accordion-content">
        <textarea name="Text1" cols="40" rows="5" class="uk-input uk-input-small uk-input-width input notes-input" placeholder="notes"></textarea>
        </div>
        </li>
        </ul>"""
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
