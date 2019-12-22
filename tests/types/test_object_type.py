from graphql import build_schema as schema

from diff.compare import SchemaComparator


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
    assert diff[0].message() == "Field `b` was added to object type `MyType`"

    diff = SchemaComparator(b, a).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "Field `b` was removed from object type `MyType`"
