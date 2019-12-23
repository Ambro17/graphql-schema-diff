from graphql import build_schema as schema

from schemadiff.compare import SchemaComparator


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
    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 1
    assert diff[0].message == "Field `b` was added to object type `MyType`"
    assert diff[0].path == 'MyType.b'

    diff = SchemaComparator(b, a).compare()
    assert diff and len(diff) == 1
    assert diff[0].message == "Field `b` was removed from object type `MyType`"
    assert diff[0].path == 'MyType.b'


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
    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 1
    assert diff[0].message == "Description for type `MyType` changed from `docstring` to `my new docstring`"
    assert diff[0].path == 'MyType'


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
    diff = SchemaComparator(atype, input_type).compare()
    assert diff and len(diff) == 1
    assert diff[0].message == "`MyType` kind changed from `OBJECT` to `INPUT OBJECT`"
    assert diff[0].path == 'MyType'
