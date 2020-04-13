from graphql import build_schema as schema

from schemadiff.changes import Criticality
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
    assert diff[0].criticality == Criticality.safe()


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
    assert diff[0].criticality == Criticality.breaking(
        'Removing a type is a breaking change. It is preferred to '
        'deprecate and remove all references to this type first.'
    )


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
    assert diff[0].criticality == Criticality.breaking(
        'Changing a field type will break queries that assume its type'
    )


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
    assert diff[0].message == "`QueryParams` kind changed from `INPUT OBJECT` to `OBJECT`"
    assert diff[0].criticality == Criticality.breaking(
        'Changing the kind of a type is a breaking change because '
        'it can cause existing queries to error. For example, '
        'turning an object type to a scalar type would break queries '
        'that define a selection set for this type.'
    )


def test_schema_query_root_changed():
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
        query: ChangedQuery
    }

    type ChangedQuery {
        field: String!
    }
    """)
    diff = Schema(old_schema, new_schema).diff()
    print(diff)
    assert diff and len(diff) == 3
    assert {x.message for x in diff} == {
        'Type `ChangedQuery` was added',
        'Type `Query` was removed',
        'Schema query root has changed from `Query` to `ChangedQuery`'
    }


def test_schema_mutation_root_changed():
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
        mutation: Mutation
    }

    type Query {
        field: String!
    }

    type Mutation {
        my_mutation: Int
    }
    """)
    diff = Schema(old_schema, new_schema).diff()
    print(diff)
    assert diff and len(diff) == 2
    assert {x.message for x in diff} == {
        'Type `Mutation` was added',
        'Schema mutation root has changed from `None` to `Mutation`'
    }


def test_schema_suscription_root_changed():
    old_schema = schema("""
    schema {
        query: Query
        subscription: Subscription
    }

    type Query {
        field: String!
    }

    type Subscription {
        a: Int
    }
    """)
    new_schema = schema("""
    schema {
        query: Query
        subscription: ChangedSubscription
    }

    type Query {
        field: String!
    }

    type ChangedSubscription {
        a: Int
    }

    type Subscription {
        a: Int
    }
    """)
    diff = Schema(old_schema, new_schema).diff()
    print(diff)
    assert diff and len(diff) == 2
    assert {x.message for x in diff} == {
        'Type `ChangedSubscription` was added',
        'Schema subscription root has changed from `Subscription` to `ChangedSubscription`'
    }
