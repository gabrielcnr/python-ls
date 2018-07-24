# python-ls
A better replacement for Python's built-in `dir` function with searching in mind.

Sometimes when you're developing using Python's interactive shell, or IPython, or working with a Jupyter Notebook or even debugging using pdb, you find yourself having to navigate through complex object structures. If you're not entirely familiar with the class in hand you usually have two options: resort to the documentation of the libraries and projects you're working with, or put the explorer's hat on and go down a trial-and-error route, using Python's builtin `dir` function to see which attributes and functions an object may have and then take a good guess on the next object you will be inspecting.

There must be a better way, right?

Well, now yes, you have `ls` to help you with that task. If you have rough idea of what you're looking for, you can search for that "thing" by name (fingers crossed here: hopefully the developers of the APIs/libraries you're dealing with were careful enough about their naming conventions). Even if (often) your target object may be a few levels deep down the object structure.

`ls` goes recursively through your object structure, it tries to visit attributes searching for the name you're looking for. It also considers dictionary keys if it stumbles across dictionaries, and in the end it prints out the matching occurrences and tells you their types too.

```python
>>> ls(ls, 'code', depth=3)
func_code                                                                             code
func_code.co_code                                                                      str    200
func_code.co_code.decode()                                      builtin_function_or_method
func_code.co_code.encode()                                      builtin_function_or_method
func_code.co_filename.decode()                                  builtin_function_or_method
func_code.co_filename.encode()                                  builtin_function_or_method
func_code.co_lnotab.decode()                                    builtin_function_or_method
func_code.co_lnotab.encode()                                    builtin_function_or_method
func_code.co_name.decode()                                      builtin_function_or_method
func_code.co_name.encode()                                      builtin_function_or_method
func_globals['xdir'].func_code                                                        code
func_globals['iter_ls'].func_code                                                     code
```

# Install

`pip install python-ls`

# `ls` available as builtin

`python-ls` will inject the `ls` function in the `__builtin__` namespace at installation step.

It does this by using a `.pth` file which simply performs that injection.

# Security

If you're running this against objects that have properties, lazy attributes or any other dynamic code, keep in mind that `ls` will try to fetch the value of the property/lazy attribute using `getattr()`. This will cause the body of the function to be executed, so you can imagine already the potential hazard here, right?

**TODO: make a default `unsafe=False` kwarg and then only visit properties if `unsafe` is explicitly set to `True`.**

# About the name `ls`

Python has `dir` as a builtin. The equivalent of that command-line command in GNU/Linux world is `ls`. We had considered calling it `xdir`, which by the way is a function that works like `dir()` by returning a list of occurrences to you.

# Contribute!

Please send your issues, bug reports and, even more welcome, your Pull Requests ;-)

Enjoy!
