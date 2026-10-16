""" Quickly hide/show elements without touching pyscript.

    from senza.visibility import hide, show, toggle, is_hidden

    hide(my_dialog)            # element stays in the DOM, just display:none
    show(my_dialog)
    toggle(my_button)          # flip; toggle(el, show=True/False) to be explicit
    if is_hidden(my_panel): ...

Works on `pyscript.web` Elements and ElementCollections. The implementation is
a single `.senza-hidden { display: none !important }` rule injected into the
page head on first use, so it composes with your own CSS (and beats utility
rules of lower specificity).
"""

from typing import Iterable, Optional, Union

from pyscript import web

HIDDEN_CLASS = "senza-hidden"

_RULE = f".{HIDDEN_CLASS} {{ display: none !important; }}"
_css_installed = False


def _ensure_css() -> None:
    global _css_installed
    if _css_installed:
        return
    style = web.style(_RULE, id="senza-visibility")
    web.page.head.append(style)
    _css_installed = True


def _elements_of(*items: Union[web.Element, web.ElementCollection, Iterable]):
    for item in items:
        if isinstance(item, web.ElementCollection):
            yield from item
        elif isinstance(item, web.Element):
            yield item
        else:  # any iterable of elements
            yield from item


def hide(*elements: Union[web.Element, web.ElementCollection, Iterable]) -> None:
    """Hide the given elements (visually; they remain in layout source)."""
    _ensure_css()
    for element in _elements_of(*elements):
        element.classes.add(HIDDEN_CLASS)


def show(*elements: Union[web.Element, web.ElementCollection, Iterable]) -> None:
    """Show the given elements (no error if not hidden)."""
    _ensure_css()
    for element in _elements_of(*elements):
        element.classes.discard(HIDDEN_CLASS)


def is_hidden(element: web.Element) -> bool:
    """True if the element is hidden by senza (or otherwise has display:none)."""
    return HIDDEN_CLASS in element.classes or element.style.get("display") == "none"


def toggle(element: web.Element, show_: Optional[bool] = None) -> None:
    """Flip an element's visibility. Pass `show_=True/False` to force a state."""
    want_visible: Optional[bool] = show_ if show_ is not None else is_hidden(element)
    (show if want_visible else hide)(element)