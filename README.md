# python-ls

A smarter replacement for Python's built-in `dir()` — built for exploring objects interactively.

[![PyPI](https://img.shields.io/pypi/v/python-ls.svg)](https://pypi.python.org/pypi/python-ls)
[![PythonVersions](https://img.shields.io/pypi/pyversions/python-ls.svg)](https://pypi.python.org/pypi/python-ls)

## What problem does it solve?

When working in a Python REPL, IPython session, Jupyter Notebook, or a `pdb` debugging session, you often need to explore unfamiliar objects. Python's built-in `dir()` gives you a flat list of attribute names — but it doesn't search, it doesn't recurse, and it tells you nothing about types or sizes.

`ls` fixes that. Given an object and a search term, it walks the object's attribute tree recursively, finds anything whose name contains your term, and prints the results with their types and sizes.

## Install

```
pip install python-ls
```

After installation, `ls` is automatically injected into Python's `builtins`, so it's available in any interactive session without any import.

## Usage

### Basic: list top-level attributes

```python
>>> ls(my_obj)
```

### Search by name across the object tree

```python
>>> ls(my_obj, "price", depth=3)
order.items[0].price                                           float
order.items[1].price                                           float
order.discount.price_threshold                                 float
```

### Control recursion depth

```python
>>> ls(my_obj, depth=2)   # explore 2 levels deep
>>> ls(my_obj, "name")    # search unlimited depth (depth defaults to None when attr is given)
```

### Include private attributes

```python
>>> ls(my_obj, under=False)    # include _single_underscore attributes
>>> ls(my_obj, dunder=True)    # include __dunder__ attributes
```

### Get results as a list instead of printing

```python
>>> xdir(my_obj, "price", depth=3)
['order.items[0].price', 'order.items[1].price', 'order.discount.price_threshold']
```

### Use the generator directly

```python
>>> for path, value in iter_ls(my_obj, "price", depth=3):
...     print(path, value)
```

## Explicit import

If you prefer to import explicitly rather than rely on the builtin injection:

```python
from python_ls import ls, xdir, iter_ls
```

## pandas support

`ls` handles `pandas.DataFrame` objects specially — it searches column names rather than object attributes.

```python
>>> ls(df, "revenue", depth=2)
```

## A note on safety

`ls` uses `getattr()` to retrieve attribute values, which will execute any property or lazy attribute code. If you're exploring objects with side-effectful properties, be aware that those will run. A future `unsafe=False` flag to skip properties is planned.

## API

| Function | Description |
|---|---|
| `ls(obj, attr=None, depth=None, dunder=False, under=True)` | Print matching attributes with type and size |
| `xdir(obj, attr=None, depth=None, dunder=False, under=True)` | Return matching attribute paths as a list |
| `iter_ls(obj, attr=None, depth=None, ...)` | Generator yielding `(path, value)` pairs |

## Contribute

Issues, bug reports, and pull requests are welcome at https://github.com/gabrielcnr/python-ls.
