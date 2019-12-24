from graphql import build_schema as schema

from schemadiff.diff.schema import Schema


def test_schema_no_diff():
    a_schema = schema("""
    schema {
        query: Query
    }
    type Query {
        a: String!
    }
    """)
    diff = Schema(a_schema, a_schema).diff()
    assert diff == []


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
    diff = Schema(old_schema, new_schema).diff()
    assert diff and len(diff) == 1
    # Type Int was also added but its ignored because its a primitive.
    assert diff[0].message == "Type `AddedType` was added"


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
    diff = Schema(old_schema, new_schema).diff()
    assert diff and len(diff) == 1
    # Type Int was also removed but it is ignored because it's a primitive.
    assert diff[0].message == "Type `ToBeRemovedType` was removed"


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
    diff = Schema(old_schema, new_schema).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "`Query.field` type changed from `String!` to `Int!`"


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
    diff = Schema(old_schema, new_schema).diff()
    assert diff and len(diff) == 2
    expected_changes = {
        "Type `Query` was removed",
        "Type `NotTheSameQuery` was added"
    }
    for change in diff:
        assert change.message in expected_changes


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
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    for change in diff:
        assert change.message == "`QueryParams` kind changed from `INPUT OBJECT` to `OBJECT`"
