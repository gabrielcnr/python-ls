import builtins

from ._ls import PropertyInfo, iter_ls, ls, xdir

__all__ = ["PropertyInfo", "iter_ls", "ls", "xdir"]

builtins.ls = ls  # type: ignore[attr-defined]
