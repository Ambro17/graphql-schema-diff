from graphql import build_schema as schema

from schemadiff.restrictions import (
    RestrictAddingFieldsWithoutDescription,
    RestrictAddingTypeWithoutDescription,
    RestrictAddingEnumWithoutDescription,
    RestrictRemovingEnumValueDescription,
    RestrictRemovingTypeDescription,
)
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
    assert RestrictAddingTypeWithoutDescription.is_restricted(diff[0]) is False


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
    assert RestrictAddingTypeWithoutDescription.is_restricted(diff[0]) is True


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
    assert RestrictRemovingTypeDescription.is_restricted(diff[0]) is True

    diff = Schema(a, c).diff()
    assert RestrictRemovingTypeDescription.is_restricted(diff[0]) is True


def test_field_added_without_desc():
    a = schema("""
    type MyType{
        a: Int
    }
    """)
    b = schema("""
    type MyType{
        a: Int
        b: String!
    }
    """)
    c = schema("""
    type MyType{
        a: Int
        \"\"\"WithDesc\"\"\"
        b: String!
    }
    """)
    diff = Schema(a, b).diff()
    assert RestrictAddingFieldsWithoutDescription.is_restricted(diff[0]) is True

    diff = Schema(a, c).diff()
    assert RestrictAddingFieldsWithoutDescription.is_restricted(diff[0]) is False


def test_enum_added_without_desc():
    a = schema("""
    enum Letters {
        A
    }
    """)
    b = schema("""
    enum Letters {
        A
        B
    }
    """)
    c = schema("""
    enum Letters {
        A
        \"\"\"WithDesc\"\"\"
        B
    }
    """)
    diff = Schema(a, b).diff()
    assert RestrictAddingEnumWithoutDescription.is_restricted(diff[0]) is True

    diff = Schema(a, c).diff()
    assert RestrictAddingEnumWithoutDescription.is_restricted(diff[0]) is False


def test_enum_value_removing_desc():
    a = schema("""
    enum Letters {
        \"\"\"WithDesc\"\"\"
        A
    }
    """)
    b = schema("""
    enum Letters {
        A
    }
    """)
    diff = Schema(a, b).diff()
    assert RestrictRemovingEnumValueDescription.is_restricted(diff[0]) is True
