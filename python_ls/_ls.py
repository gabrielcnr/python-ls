import fnmatch
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
        if has_pandas and isinstance(value, pd.DataFrame):
            size = "{0}x{1}".format(*value.shape)
        elif hasattr(value, "__len__"):
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

                try:
                    if isinstance(obj, dict) or (has_pandas and isinstance(obj, pd.DataFrame)):
                        val = obj[a]
                    else:
                        val = getattr(obj, a)
                except Exception:
                    val = BAD

                if include(a):
                    if type is not None and val is not BAD:
                        if isinstance(type, str):
                            val_type_name = _type(val).__name__.lower()
                            if _has_glob_chars(type):
                                type_match = fnmatch.fnmatchcase(val_type_name, type.lower())
                            else:
                                type_match = type.lower() in val_type_name
                        else:
                            type_match = isinstance(val, type)
                        if not type_match:
                            continue
                    suffix = "()" if val is not BAD and callable(val) else ""
                    yield new_path + suffix, val

                if val is not BAD and not a.startswith("__"):
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
