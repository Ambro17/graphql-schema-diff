from graphql import build_schema as schema

from schemadiff.changes import Criticality
from schemadiff.diff.schema import Schema


def test_object_type_added_field():
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
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "Field `b` was added to object type `MyType`"
    assert diff[0].path == 'MyType.b'
    assert diff[0].criticality == Criticality.safe()

    diff = Schema(b, a).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "Field `b` was removed from object type `MyType`"
    assert diff[0].path == 'MyType.b'
    assert diff[0].criticality == Criticality.breaking(
        'Removing a field is a breaking change. It is preferred to deprecate the field before removing it.'
    )


def test_object_type_description_changed():
    a = schema('''
    """docstring"""
    type MyType{
        a: Int
    }
    ''')
    b = schema('''
    """my new docstring"""
    type MyType{
        a: Int
    }
    ''')
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "Description for type `MyType` changed from `docstring` to `my new docstring`"
    assert diff[0].path == 'MyType'
    assert diff[0].criticality == Criticality.safe()


def test_type_kind_change():
    atype = schema('''
    type MyType{
        a: Int
    }
    ''')
    input_type = schema('''
    input MyType{
        a: Int
    }
    ''')
    diff = Schema(atype, input_type).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "`MyType` kind changed from `OBJECT` to `INPUT OBJECT`"
    assert diff[0].path == 'MyType'
    assert diff[0].criticality == Criticality.breaking(
        'Changing the kind of a type is a breaking change because it can '
        'cause existing queries to error. For example, turning an object '
        'type to a scalar type would break queries that define a selection set for this type.'
    )
