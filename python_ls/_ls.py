import fnmatch
import typing
from collections.abc import Iterator
from typing import Any

_type = type

try:
    import pandas as pd
except ImportError:
    has_pandas = False
else:
    has_pandas = True

# sentinel for attributes that could not be retrieved
BAD = object()

_GLOB_CHARS = frozenset("*?[]")


def _has_glob_chars(pattern: str) -> bool:
    return any(c in _GLOB_CHARS for c in pattern)


class PropertyInfo:
    """Sentinel yielded for property attributes that were not evaluated."""

    __slots__ = ("type_hint",)

    def __init__(self, type_hint: type | None = None):
        self.type_hint = type_hint


def _get_mro(obj: Any) -> tuple[type, ...]:
    return obj.__mro__ if isinstance(obj, _type) else _type(obj).__mro__


def _is_property(obj: Any, attr_name: str) -> bool:
    for cls in _get_mro(obj):
        if attr_name in cls.__dict__ and isinstance(cls.__dict__[attr_name], property):
            return True
    return False


def _get_property_type_hint(obj: Any, attr_name: str) -> type | None:
    # Try class-level annotations
    owner = obj if isinstance(obj, _type) else _type(obj)
    try:
        hints = typing.get_type_hints(owner)
        if attr_name in hints:
            return hints[attr_name]
    except Exception:
        pass
    # Try the property getter's return annotation
    for cls in _get_mro(obj):
        if attr_name in cls.__dict__:
            prop = cls.__dict__[attr_name]
            if isinstance(prop, property) and prop.fget is not None:
                try:
                    hints = typing.get_type_hints(prop.fget)
                    return hints.get("return")
                except Exception:
                    pass
    return None


def _type_hint_name(hint: Any) -> str:
    if hasattr(hint, "__name__"):
        return hint.__name__
    return str(hint)


def ls(
    obj: Any,
    attr: str | None = None,
    depth: int | None = None,
    dunder: bool = False,
    under: bool = True,
    type: type | tuple[type, ...] | str | None = None,
) -> None:
    """
    Recursively search for a named attribute in an object and print matches.

    :param obj: Root object to search
    :param attr: Name (or partial name) of the attribute to search for
    :param depth: Maximum search depth, defaults to 1 (no recursion)
    :param dunder: If True, double-underscore prefixed attributes are included (default: excluded)
    :param under: If True, single-underscore prefixed attributes are included (default: included)
    """
    if depth is None:
        depth = 1

    for attr_path, value in iter_ls(obj, attr=attr, depth=depth, dunder=dunder, under=under, type=type):
        size: int | str = ""
        if isinstance(value, PropertyInfo):
            if value.type_hint is not None:
                type_name = f"property[{_type_hint_name(value.type_hint)}]"
            else:
                type_name = "property"
        elif has_pandas and isinstance(value, pd.DataFrame):
            size = "{0}x{1}".format(*value.shape)
            type_name = _type(value).__name__
        else:
            if hasattr(value, "__len__"):
                size = len(value)
            type_name = _type(value).__name__
        print("{:<60}{:>20}{:>7}".format(attr_path, type_name, size))


def xdir(
    obj: Any,
    attr: str | None = None,
    depth: int | None = None,
    dunder: bool = False,
    under: bool = True,
    type: type | tuple[type, ...] | str | None = None,
) -> list[str]:
    """
    Like ls() but returns a list of matching attribute paths instead of printing.

    :param obj: Root object to search
    :param attr: Name (or partial name) of the attribute to search for
    :param depth: Maximum search depth
    :param dunder: If True, double-underscore prefixed attributes are included
    :param under: If True, single-underscore prefixed attributes are included
    :return: List of matching attribute path strings
    """
    if depth is None and attr is None:
        depth = 1
    return [path for path, _ in iter_ls(obj, attr=attr, depth=depth, dunder=dunder, under=under, type=type)]


def iter_ls(
    obj: Any,
    attr: str | None = None,
    depth: int | None = 1,
    dunder: bool = False,
    under: bool = True,
    type: type | tuple[type, ...] | str | None = None,
    visited: set[int] | None = None,
    current_depth: int = 1,
    path: str = "",
) -> Iterator[tuple[str, Any]]:
    """
    Generator that recursively yields (path, value) pairs for matching attributes.

    :param obj: Root object to search
    :param attr: Name (or partial name) of the attribute to search for
    :param depth: Maximum search depth (None for unlimited)
    :param dunder: If True, double-underscore prefixed attributes are included
    :param under: If True, single-underscore prefixed attributes are included
    :param visited: Set of visited object IDs (used internally to avoid cycles)
    :param current_depth: Current recursion depth (used internally)
    :param path: Accumulated attribute path (used internally)
    """
    visited = visited or set()

    if (depth is None) or (current_depth <= depth):
        if id(obj) not in visited:
            visited.add(id(obj))

            filters: list = []

            def include(a: str) -> bool:
                return all(f(a) for f in filters)

            if attr:
                if _has_glob_chars(attr):
                    attr_lower = attr.lower()
                    filters.append(lambda a: fnmatch.fnmatchcase(a.lower(), attr_lower))
                else:
                    attr_lower = attr.lower()
                    filters.append(lambda a: attr_lower in a.lower())

            if not dunder:
                filters.append(lambda a: not a.startswith("__"))

            if not under:
                filters.append(lambda a: not a.startswith("_"))

            if isinstance(obj, dict):
                attrs = [str(k) for k in obj.keys()]
            elif has_pandas and isinstance(obj, pd.DataFrame):
                attrs = [str(c) for c in obj.columns]
            else:
                attrs = dir(obj)

            for a in attrs:
                if isinstance(obj, dict) or (has_pandas and isinstance(obj, pd.DataFrame)):
                    new_path = path + "[%r]" % a
                else:
                    new_path = ".".join([path, a]) if path else a

                is_dict_like = isinstance(obj, dict) or (has_pandas and isinstance(obj, pd.DataFrame))

                try:
                    if is_dict_like:
                        val = obj[a]
                    elif _is_property(obj, a):
                        hint = _get_property_type_hint(obj, a)
                        val = PropertyInfo(type_hint=hint)
                    else:
                        val = getattr(obj, a)
                except Exception:
                    val = BAD

                if include(a):
                    if type is not None and val is not BAD:
                        if isinstance(val, PropertyInfo):
                            if val.type_hint is not None:
                                if isinstance(type, str):
                                    hint_name = _type_hint_name(val.type_hint).lower()
                                    if _has_glob_chars(type):
                                        type_match = fnmatch.fnmatchcase(hint_name, type.lower())
                                    else:
                                        type_match = type.lower() in hint_name
                                else:
                                    try:
                                        type_match = issubclass(val.type_hint, type)
                                    except TypeError:
                                        type_match = False
                            else:
                                type_match = False
                        elif isinstance(type, str):
                            val_type_name = _type(val).__name__.lower()
                            if _has_glob_chars(type):
                                type_match = fnmatch.fnmatchcase(val_type_name, type.lower())
                            else:
                                type_match = type.lower() in val_type_name
                        else:
                            type_match = isinstance(val, type)
                        if not type_match:
                            continue
                    suffix = "()" if val is not BAD and not isinstance(val, PropertyInfo) and callable(val) else ""
                    yield new_path + suffix, val

                if val is not BAD and not a.startswith("__"):
                    if isinstance(val, PropertyInfo):
                        # Best-effort: recurse into the type hint's class namespace
                        if val.type_hint is not None and isinstance(val.type_hint, _type):
                            yield from iter_ls(
                                val.type_hint,
                                attr=attr,
                                depth=depth,
                                dunder=dunder,
                                under=under,
                                type=type,
                                visited=visited,
                                current_depth=current_depth + 1,
                                path=new_path,
                            )
                        continue
                    yield from iter_ls(
                        val,
                        attr=attr,
                        depth=depth,
                        dunder=dunder,
                        under=under,
                        type=type,
                        visited=visited,
                        current_depth=current_depth + 1,
                        path=new_path,
                    )
