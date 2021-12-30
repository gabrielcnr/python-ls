import pytest

from python_ls import iter_ls


class Object(object):
    pass


class Universe:
    @property
    def answer(self):
        return 41 + 1


@pytest.fixture
def test_obj():
    o = Object()
    o.foo = Object()
    o.foo.bar = Object()
    o.foo.bar.something = Object()
    o.foo.bar.aaa = Object()
    o.foo.bar.bbb = Object()
    o.foo.bar._something_else = dict  # a callable (lambda recurses infinitely in Python 2.7 when depth=None)
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


def test_depth_is_None(test_obj):
    expected = [
        'foo.bar._something_else()',
        'foo.bar.something',
        "foo.baz['something_weird']",
        'lala.something',
    ]

    actual = [x[0] for x in iter_ls(test_obj, 'something', depth=None)]
    assert actual == expected


def test_ls_unsafe():
    actual = list(iter_ls(Universe(), unsafe=True))
    assert ('answer', 42) in actual


def test_ls_safe():
    actual = list(iter_ls(Universe()))
    assert ('answer', 42) not in actual
