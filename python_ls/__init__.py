from ._ls import iter_ls, ls, xdir


__all__ = ['iter_ls', 'ls', 'xdir']


def _inject_builtin():
    import sys
    if sys.version_info.major == 2:
        import __builtin__ as builtins
    else:
        import builtins

    builtins.ls = ls


_inject_builtin()
