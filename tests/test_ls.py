from python_ls import iter_ls
from python_ls._ls import _has_glob_chars
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


class TestHasGlobChars:
    def test_plain_string(self):
        assert not _has_glob_chars("something")

    def test_star(self):
        assert _has_glob_chars("get_*")

    def test_question_mark(self):
        assert _has_glob_chars("fo?")

    def test_brackets(self):
        assert _has_glob_chars("[abc]")


class TestAttrGlobPattern:
    def test_star_prefix(self, test_obj):
        """*thing should match 'something' but not via substring."""
        attrs = [path.split(".")[-1] for path, _ in iter_ls(test_obj, "*oo", depth=1)]
        assert attrs == ["foo"]

    def test_star_suffix(self, test_obj):
        attrs = [path for path, _ in iter_ls(test_obj, "la*", depth=1)]
        assert attrs == ["lala"]

    def test_star_middle(self, test_obj):
        """Glob *a* at depth=2 matches bar, baz, lala, lele via fnmatch."""
        attrs = [path.split(".")[-1].rstrip("()") for path, _ in iter_ls(test_obj, "*a*", depth=2)]
        assert "bar" in attrs
        assert "baz" in attrs

    def test_question_mark(self, test_obj):
        attrs = [path for path, _ in iter_ls(test_obj, "fo?", depth=2)]
        assert "foo" in attrs

    def test_character_class(self, test_obj):
        attrs = [path.split(".")[-1] for path, _ in iter_ls(test_obj, "[fb]*", depth=2)]
        assert "foo" in attrs
        assert "bar" in attrs
        assert "baz" in attrs

    def test_plain_attr_still_does_substring(self, test_obj):
        """Plain string without glob chars should still do substring matching."""
        attrs = [path.split(".")[-1].rstrip("()") for path, _ in iter_ls(test_obj, "omethin", depth=2)]
        assert "something" in attrs

    def test_case_insensitive_substring(self, test_obj):
        attrs = [path for path, _ in iter_ls(test_obj, "FOO", depth=1)]
        assert "foo" in attrs

    def test_case_insensitive_glob(self, test_obj):
        attrs = [path for path, _ in iter_ls(test_obj, "FO*", depth=1)]
        assert "foo" in attrs

