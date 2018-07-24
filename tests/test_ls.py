from python_ls import iter_ls
import pytest


class Object(object):
    pass


@pytest.fixture
def test_obj():
    o = Object()
    o.foo = Object()
    o.foo.bar = Object()
    o.foo.bar.something = Object()
    o.foo.bar.aaa = Object()
    o.foo.bar.bbb = Object()
    o.foo.bar._something_else = lambda: None
    o.foo.baz = {'something_weird': 'going on', 'blah': 'bleh'}

    o.lala = Object()
    o.lala.lele = Object()
    o.lala.something = Object()
    return o


def test_ls_no_recursion(test_obj):
    expected = ['foo', 'lala']
    actual = [x[0] for x in iter_ls(test_obj)]
    assert actual == expected


def test_ls_recursive(test_obj):
    expected = [
        'foo.bar._something_else()',
        'foo.bar.something',
        "foo.baz['something_weird']",
        'lala.something',
    ]

    actual = [x[0] for x in iter_ls(test_obj, 'something', depth=4)]
    assert actual == expected
