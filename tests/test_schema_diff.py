import pytest
from graphql import build_schema as schema

from diff.compare import SchemaComparator


def test_schema_no_diff():
    a_schema = schema("""
    schema {
        query: Query
    }
    type Query {
        a: String!
    }
    """)
    diff = SchemaComparator(a_schema, a_schema).compare()
    expected_diff = []
    assert diff == expected_diff


def test_schema_added_type():
    old_schema = schema("""
    schema {
        query: Query
    }

    type Query {
        field: String!
    }
    """)
    new_schema = schema("""
    schema {
        query: Query
    }

    type Query {
        field: String!
    }

    type AddedType {
        added: Int
    }
    """)
    diff = SchemaComparator(old_schema, new_schema).compare()
    expected_diff = [
        "Type `AddedType` was added",  # Type Int was also added but its ignored because its a primitive.
    ]
    assert [x.message() for x in diff] == expected_diff


def test_schema_removed_type():
    old_schema = schema("""
    schema {
        query: Query
    }

    type Query {
        field: String!
    }
    
    type ToBeRemovedType {
        added: Int
    }
    
    """)
    new_schema = schema("""
    schema {
        query: Query
    }

    type Query {
        field: String!
    }
    """)
    diff = SchemaComparator(old_schema, new_schema).compare()
    expected_diff = [
        "Type `ToBeRemovedType` was removed",  # Type Int was also removed but it is ignored because it's a primitive.
    ]
    assert [x.message() for x in diff] == expected_diff


def test_schema_query_fields_type_has_changes():
    old_schema = schema("""
    schema {
        query: Query
    }

    type Query {
        field: String!
    }
    """)
    new_schema = schema("""
    schema {
        query: Query
    }

    type Query {
        field: Int!
    }
    """)
    diff = SchemaComparator(old_schema, new_schema).compare()
    expected_diff = [
        "Field `Query.field` changed type from `String!` to `Int!`"
    ]
    assert [x.message() for x in diff] == expected_diff


def test_schema_query_root_changed():
    old_schema = schema('''
    schema {
        query: Query
    }

    type Query {
        field: String!
    }
    ''')
    new_schema = schema('''
    schema {
        query: NotTheSameQuery
    }

    type NotTheSameQuery {
        field: String!
    }
    ''')
    diff = SchemaComparator(old_schema, new_schema).compare()
    assert diff and len(diff) == 2
    assert False


def test_named_typed_changed_type():
    a = schema("""
    input QueryParams {
        a: String!
    }
    """)
    b = schema("""
    type QueryParams {
        a: String!
    }
    """)
    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 1
    for change in diff:
        assert change.message() == "`QueryParams` kind changed from `INPUT OBJECT` to `OBJECT`"
