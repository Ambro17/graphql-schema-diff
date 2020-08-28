from graphql import build_schema as schema

from schemadiff.restrictions import RestrictAddingWithoutDescription, RestrictRemovingDescription
from schemadiff.diff.schema import Schema


def test_type_added_with_desc():
    a = schema("""
    type MyType{
        a: Int
    }
    """)
    b = schema("""
    type MyType{
        a: Int
    }
    \"\"\"This has desc\"\"\"
    type NewType{
        b: String!
    }
    """)
    diff = Schema(a, b).diff()
    assert RestrictAddingWithoutDescription.is_restricted(diff[0]) is False


def test_type_added_without_desc():
    a = schema("""
    type MyType{
        a: Int
    }
    """)
    b = schema("""
    type MyType{
        a: Int
    }
    type NewType{
        b: String!
    }
    """)
    diff = Schema(a, b).diff()
    assert RestrictAddingWithoutDescription.is_restricted(diff[0]) is True


def test_type_changed_desc_removed():
    a = schema("""
    \"\"\"This has desc\"\"\"
    type MyType{
        a: Int
    }
    """)
    b = schema("""
    type MyType{
        a: Int
    }
    """)
    c = schema("""
    \"\"\"\"\"\"
    type MyType{
        a: Int
    }
    """)
    diff = Schema(a, b).diff()
    assert RestrictRemovingDescription.is_restricted(diff[0]) is True

    diff = Schema(a, c).diff()
    assert RestrictRemovingDescription.is_restricted(diff[0]) is True
