import pytest
from graphql import build_schema as schema

from schemadiff.changes import Change, Criticality
from schemadiff.restrictions import (
    Restriction,
    RestrictAddingFieldsWithoutDescription,
    RestrictAddingTypeWithoutDescription,
    RestrictAddingEnumWithoutDescription,
    RestrictRemovingEnumValueDescription,
    RestrictRemovingTypeDescription,
)
from schemadiff.diff.schema import Schema


@pytest.mark.parametrize('restriction', Restriction.__subclasses__())
def test_is_restricted_defaults_to_false_for_any_other_change(restriction):
    class UnexpectedChange(Change):
        criticality = Criticality.safe()

        @property
        def message(self):
            return ""

        @property
        def path(self):
            return ""

    assert restriction.is_restricted(UnexpectedChange()) is False


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
    '''This has desc'''
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
    '''This has desc'''
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
    ''''''
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
        '''WithDesc'''
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
        '''WithDesc'''
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
        '''WithDesc'''
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
