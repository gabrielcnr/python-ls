from ._ls import iter_ls, ls, xdir

try:
    import __builtin__ as builtins # python 2.7
except:
    import builtins # python 3

# injecting the name ls in the builtin namespace
builtins.ls = ls
