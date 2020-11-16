from python_ls import iter_ls, ls
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
    # a callable (lambda recurses infinitely in Python 2.7 when depth=None)
    o.foo.bar._something_else = dict
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


def test_basic_ls_usage(test_obj, capsys):
    ls(test_obj, 'something')
    out, err = capsys.readouterr()
    expect = [
        ['foo.bar._something_else()', 'type'],
        ['foo.bar.something', 'Object'],
        ["foo.baz['something_weird']", 'str', '8'],
        ['lala.something', 'Object']
    ]
    assert expect == [line.split() for line in out.splitlines()]

