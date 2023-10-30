from pyscript import display, document, window
from pyweb import pydom
from pyweb.pydom import Element

# from out import pydom
# from out.pydom import Element


class SideBar(Element):
    """Base component builder for an HTML button component.
    __Contains__
    id
    class
    inner_text
    """

    _type = "div"
    _class_list: set = {"container"}

    _color_list: dict[str] = {    }

    def __folders__(self) -> str:
        opt_list = ""
        for id, folder in self._color_list.items():
            opt_list += f"""
                <li class="uk-active" id="{id}">
                {folder}
                </li>"""
        return opt_list

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
        self.html = f"""
        <div id="offcanvas-reveal" uk-offcanvas="mode: reveal; overlay: true">
        <div class="uk-offcanvas-bar">
        <button class="uk-offcanvas-close" type="button" uk-close></button>
        <ul id="sidebar-list">
        {self.__folders__()}
        </li>
        </ul>
        </div>
        </div>"""
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
