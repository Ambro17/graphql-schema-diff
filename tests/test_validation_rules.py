import pytest
from graphql import build_schema as schema

from schemadiff.changes import Change, Criticality
from schemadiff.validation_rules import (
    ValidationRule,
    AddFieldWithoutDescription,
    AddTypeWithoutDescription,
    AddEnumValueWithoutDescription,
    RemoveEnumValueDescription,
    RemoveTypeDescription,
)
from schemadiff.diff.schema import Schema


@pytest.mark.parametrize('rule', ValidationRule.__subclasses__())
def test_is_valid_defaults_to_true_for_any_other_change(rule):
    class UnexpectedChange(Change):
        criticality = Criticality.safe()

        @property
        def message(self):
            return ""

        @property
        def path(self):
            return ""

    assert rule(UnexpectedChange()).is_valid() is True


def test_type_added_with_desc():
    a = schema('''
    type MyType{
        a: Int
    }
    ''')
    b = schema('''
    type MyType{
        a: Int
    }
    """This has desc"""
    type NewType{
        b: String!
    }
    ''')
    diff = Schema(a, b).diff()
    assert AddTypeWithoutDescription(diff[0]).is_valid() is True


def test_type_added_without_desc():
    a = schema('''
    type MyType{
        a: Int
    }
    ''')
    b = schema('''
    type MyType{
        a: Int
    }
    type NewType{
        b: String!
    }
    ''')
    diff = Schema(a, b).diff()
    assert AddTypeWithoutDescription(diff[0]).is_valid() is False


def test_type_changed_desc_removed():
    a = schema('''
    """This has desc"""
    type MyType{
        a: Int
    }
    ''')
    b = schema('''
    type MyType{
        a: Int
    }
    ''')
    c = schema('''
    """"""
    type MyType{
        a: Int
    }
    ''')
    diff = Schema(a, b).diff()
    assert RemoveTypeDescription(diff[0]).is_valid() is False

    diff = Schema(a, c).diff()
    assert RemoveTypeDescription(diff[0]).is_valid() is False


def test_field_added_without_desc():
    a = schema('''
    type MyType{
        a: Int
    }
    ''')
    b = schema('''
    type MyType{
        a: Int
        b: String!
    }
    ''')
    c = schema('''
    type MyType{
        a: Int
        """WithDesc"""
        b: String!
    }
    ''')
    diff = Schema(a, b).diff()
    assert AddFieldWithoutDescription(diff[0]).is_valid() is False

    diff = Schema(a, c).diff()
    assert AddFieldWithoutDescription(diff[0]).is_valid() is True


def test_enum_added_without_desc():
    a = schema('''
    enum Letters {
        A
    }
    ''')
    b = schema('''
    enum Letters {
        A
        B
    }
    ''')
    c = schema('''
    enum Letters {
        A
        """WithDesc"""
        B
    }
    ''')
    diff = Schema(a, b).diff()
    assert AddEnumValueWithoutDescription(diff[0]).is_valid() is False

    diff = Schema(a, c).diff()
    assert AddEnumValueWithoutDescription(diff[0]).is_valid() is True


def test_enum_value_removing_desc():
    a = schema('''
    enum Letters {
        """WithDesc"""
        A
    }
    ''')
    b = schema('''
    enum Letters {
        A
    }
    ''')
    diff = Schema(a, b).diff()
    assert RemoveEnumValueDescription(diff[0]).is_valid() is False
