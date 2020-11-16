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
    o.foo.bar._something_else = lambda: None
    o.foo.bar.someconstructor_obj = dict
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


def test_iter_ls_constructor_obj(test_obj):
    expected = ['foo.bar.someconstructor_obj()']
    actual = [x[0] for x in iter_ls(test_obj, 'someconstructor', depth=None)]
    assert actual == expected


def test_basic_ls_usage(test_obj, capsys):
    ls(test_obj, 'something')
    out, err = capsys.readouterr()
    expect = [
        ['foo.bar._something_else()', 'function'],
        ['foo.bar.something', 'Object'],
        ["foo.baz['something_weird']", 'str', '8'],
        ['lala.something', 'Object']
    ]
    assert expect == [line.split() for line in out.splitlines()]


def test_ls_constructor_obj(test_obj, capsys):
    ls(test_obj, 'someconstructor')
    out, err = capsys.readouterr()
    expect = [['foo.bar.someconstructor_obj()', 'type']]
    assert expect == [line.split() for line in out.splitlines()]

