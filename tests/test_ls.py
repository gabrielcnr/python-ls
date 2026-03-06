from python_ls import PropertyInfo, iter_ls
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


class TestTypeFilter:
    def test_filter_by_single_type(self):
        o = Object()
        o.x = 42
        o.y = "hello"
        o.z = 3.14
        result = [path for path, _ in iter_ls(o, type=int)]
        assert result == ["x"]

    def test_filter_by_tuple_of_types(self):
        o = Object()
        o.x = 42
        o.y = "hello"
        o.z = 3.14
        result = [path for path, _ in iter_ls(o, type=(int, str))]
        assert result == ["x", "y"]

    def test_filter_by_string(self):
        o = Object()
        o.x = 42
        o.y = "hello"
        o.z = 3.14
        result = [path for path, _ in iter_ls(o, type="int")]
        assert result == ["x"]

    def test_filter_by_string_case_insensitive(self):
        o = Object()
        o.x = 42
        o.y = "hello"
        result = [path for path, _ in iter_ls(o, type="INT")]
        assert result == ["x"]

    def test_filter_by_glob_pattern(self):
        o = Object()
        o.a = Object()
        o.b = 42
        o.c = "hello"
        result = [path for path, _ in iter_ls(o, type="Obj*")]
        assert result == ["a"]

    def test_combined_attr_and_type(self):
        o = Object()
        o.foo_int = 42
        o.foo_str = "hello"
        o.bar_int = 99
        result = [path for path, _ in iter_ls(o, attr="foo", type=int)]
        assert result == ["foo_int"]


class TestPropertySafety:
    def test_property_not_evaluated(self):
        """Property getter should not be called during ls."""
        class Obj:
            @property
            def dangerous(self) -> str:
                raise RuntimeError("should not be called")

        result = list(iter_ls(Obj()))
        paths = [p for p, _ in result]
        assert "dangerous" in paths
        val = next(v for p, v in result if p == "dangerous")
        assert isinstance(val, PropertyInfo)

    def test_property_with_return_type_hint(self):
        """PropertyInfo should carry the type hint from the getter."""
        class Obj:
            @property
            def name(self) -> str:
                return "hello"

        result = list(iter_ls(Obj()))
        val = next(v for p, v in result if p == "name")
        assert isinstance(val, PropertyInfo)
        assert val.type_hint is str

    def test_property_without_type_hint(self):
        """PropertyInfo with no annotation should have type_hint=None."""
        class Obj:
            @property
            def name(self):
                return "hello"

        result = list(iter_ls(Obj()))
        val = next(v for p, v in result if p == "name")
        assert isinstance(val, PropertyInfo)
        assert val.type_hint is None

    def test_property_class_annotation(self):
        """Type hint from class-level annotation should be picked up."""
        class Obj:
            name: int

            @property
            def name(self):
                return 42

        result = list(iter_ls(Obj()))
        val = next(v for p, v in result if p == "name")
        assert isinstance(val, PropertyInfo)
        assert val.type_hint is int

    def test_property_no_callable_suffix(self):
        """Properties should not get the '()' suffix."""
        class Obj:
            @property
            def name(self) -> str:
                return "hello"

        result = list(iter_ls(Obj()))
        paths = [p for p, _ in result]
        assert "name" in paths
        assert "name()" not in paths

    def test_property_recurse_via_type_hint(self):
        """Properties with type hints should recurse into the class namespace."""
        class Inner:
            x = 42

        class Obj:
            @property
            def inner(self) -> Inner:
                return Inner()

        result = [p for p, _ in iter_ls(Obj(), depth=3)]
        assert "inner" in result
        assert "inner.x" in result

    def test_property_type_filter_with_hint(self):
        """Type filter should work with property type hints."""
        class Obj:
            x = 42

            @property
            def name(self) -> str:
                return "hello"

        result = [p for p, _ in iter_ls(Obj(), type=str)]
        assert "name" in result

    def test_property_type_filter_string_with_hint(self):
        """String type filter should match against property type hint name."""
        class Obj:
            x = 42

            @property
            def name(self) -> str:
                return "hello"

        result = [p for p, _ in iter_ls(Obj(), type="str")]
        assert "name" in result

    def test_property_type_filter_no_hint_excluded(self):
        """Properties without type hints should be excluded by type filters."""
        class Obj:
            x = 42

            @property
            def name(self):
                return "hello"

        result = [p for p, _ in iter_ls(Obj(), type=str)]
        assert "name" not in result

    def test_inherited_property(self):
        """Properties from parent classes should be detected."""
        class Base:
            @property
            def value(self) -> int:
                raise RuntimeError("should not be called")

        class Child(Base):
            pass

        result = list(iter_ls(Child()))
        val = next(v for p, v in result if p == "value")
        assert isinstance(val, PropertyInfo)
        assert val.type_hint is int

    def test_property_recurse_into_type_hint(self):
        """When a property has a type hint, recurse into the class namespace."""
        class Inner:
            x = 42
            y = "hello"

        class Obj:
            @property
            def inner(self) -> Inner:
                raise RuntimeError("should not be called")

        result = [p for p, _ in iter_ls(Obj(), depth=2)]
        assert "inner" in result
        assert "inner.x" in result
        assert "inner.y" in result

    def test_property_recurse_search_attr(self):
        """Recursive attr search should find attributes through property type hints."""
        class Inner:
            target = 42

        class Obj:
            @property
            def inner(self) -> Inner:
                raise RuntimeError("should not be called")

        result = [p for p, _ in iter_ls(Obj(), attr="target", depth=None)]
        assert "inner.target" in result

    def test_property_recurse_no_hint_no_recursion(self):
        """Properties without type hints should not recurse."""
        class Inner:
            x = 42

        class Obj:
            @property
            def inner(self):
                raise RuntimeError("should not be called")

        result = [p for p, _ in iter_ls(Obj(), depth=2)]
        assert "inner" in result
        assert not any(p.startswith("inner.") for p in result)

    def test_property_recurse_nested_properties(self):
        """Nested properties on the hinted type should also be safe."""
        class Deep:
            z = 99

        class Inner:
            @property
            def deep(self) -> Deep:
                raise RuntimeError("should not be called")

        class Obj:
            @property
            def inner(self) -> Inner:
                raise RuntimeError("should not be called")

        result = [p for p, _ in iter_ls(Obj(), depth=3)]
        assert "inner" in result
        assert "inner.deep" in result
        assert "inner.deep.z" in result

