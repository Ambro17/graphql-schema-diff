from graphql import build_schema as schema

from schemadiff.changes import Criticality
from schemadiff.diff.schema import Schema


def test_no_field_diff():
    a = schema("""
    type Query {
        b: Int!
    }
    """)
    b = schema("""
    type Query {
        b: Int!
    }
    """)
    diff = Schema(a, b).diff()
    assert not diff


def test_field_type_changed():
    a_schema = schema("""
    type Query {
        a: String!
    }
    """)
    changed_schema = schema("""
    type Query {
        a: Int
    }
    """)
    diff = Schema(a_schema, changed_schema).diff()
    assert len(diff) == 1
    assert diff[0].message == "`Query.a` type changed from `String!` to `Int`"
    assert diff[0].path == 'Query.a'
    assert diff[0].criticality == Criticality.breaking('Changing a field type will break queries that assume its type')


def test_field_type_change_from_scalar_to_list_of_the_same_type():
    a = schema("""
    type Query {
        a: String
    }
    """)
    b = schema("""
    type Query {
        a: [String]
    }
    """)
    diff = Schema(a, b).diff()
    assert len(diff) == 1
    assert diff[0].message == "`Query.a` type changed from `String` to `[String]`"
    assert diff[0].path == 'Query.a'
    assert diff[0].criticality == Criticality.breaking('Changing a field type will break queries that assume its type')


def test_field_nullability_changed():
    a = schema("""
    type Query {
        a: Int!
    }
    """)
    b = schema("""
    type Query {
        a: Int
    }
    """)
    diff = Schema(a, b).diff()
    assert len(diff) == 1
    assert diff[0].message == "`Query.a` type changed from `Int!` to `Int`"
    assert diff[0].path == 'Query.a'
    assert diff[0].criticality == Criticality.breaking('Changing a field type will break queries that assume its type')

    diff = Schema(b, a).diff()
    assert len(diff) == 1
    assert diff[0].message == "`Query.a` type changed from `Int` to `Int!`"
    assert diff[0].path == 'Query.a'
    assert diff[0].criticality == Criticality.safe()


def test_field_type_change_nullability_change_on_lists_of_same_type():
    a = schema("""
    type Query {
        a: [Boolean]!
    }
    """)
    b = schema("""
    type Query {
        a: [Boolean]
    }
    """)
    diff = Schema(a, b).diff()
    assert len(diff) == 1
    assert diff[0].message == "`Query.a` type changed from `[Boolean]!` to `[Boolean]`"
    assert diff[0].path == 'Query.a'
    assert diff[0].criticality == Criticality.breaking('Changing a field type will break queries that assume its type')


def test_field_listof_nullability_of_inner_type_changed():
    a = schema("""
    type Query {
        a: [Int!]!
    }
    """)
    b = schema("""
    type Query {
        a: [Int]!
    }
    """)
    diff = Schema(a, b).diff()
    assert len(diff) == 1
    assert diff[0].message == "`Query.a` type changed from `[Int!]!` to `[Int]!`"
    assert diff[0].path == 'Query.a'
    assert diff[0].criticality == Criticality.breaking('Changing a field type will break queries that assume its type')


def test_field_listof_nullability_of_inner_and_outer_types_changed():
    a = schema("""
    type Query {
        a: [Float!]!
    }
    """)
    b = schema("""
    type Query {
        a: [Float]
    }
    """)
    diff = Schema(a, b).diff()
    assert len(diff) == 1
    assert diff[0].message == "`Query.a` type changed from `[Float!]!` to `[Float]`"
    assert diff[0].path == 'Query.a'
    assert diff[0].criticality == Criticality.breaking('Changing a field type will break queries that assume its type')


def test_field_list_of_inner_type_changed():
    a = schema("""
    type Query {
        a: [Float!]!
    }
    """)
    b = schema("""
    type Query {
        a: [String]
    }
    """)
    diff = Schema(a, b).diff()
    assert len(diff) == 1
    assert diff[0].message == "`Query.a` type changed from `[Float!]!` to `[String]`"
    assert diff[0].path == 'Query.a'
    assert diff[0].criticality == Criticality.breaking('Changing a field type will break queries that assume its type')


def test_description_changed():
    a = schema('''
    type Query {
        """some desc"""
        a: String
    }
    ''')
    b = schema('''
    type Query {
        """once upon a time"""
        a: String
    }
    ''')
    diff = Schema(a, b).diff()
    assert len(diff) == 1
    assert diff[0].message == "`Query.a` description changed from `some desc` to `once upon a time`"
    assert diff[0].path == 'Query.a'
    assert diff[0].criticality == Criticality.safe()


def test_deprecation_reason_changed():
    a = schema('''
    type Query {
        b: Int! @deprecated(reason: "Not used")
    }
    ''')
    b = schema('''
    type Query {
        b: Int! @deprecated(reason: "Some string")
    }
    ''')
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "Deprecation reason on field `Query.b` changed from `Not used` to `Some string`"
    assert diff[0].path == 'Query.b'
    assert diff[0].criticality == Criticality.safe()


def test_added_removed_arguments():
    a = schema("""
    type Football {
        skill: Float!
    }
    """)
    b = schema("""
    type Football {
        skill(player: ID): Float!
    }
    """)
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "Argument `player: ID` added to `Football.skill`"
    assert diff[0].path == 'Football.skill'
    assert diff[0].criticality == Criticality.safe('Adding an optional argument is a safe change')

    diff = Schema(b, a).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "Removed argument `player` from `Football.skill`"
    assert diff[0].path == 'Football.skill'
    assert diff[0].criticality == Criticality.breaking(
        'Removing a field argument will break queries that use this argument'
    )

    c = schema("""
    type Football {
        skill(player: ID, age: Int): Float!
    }
    """)
    diff = Schema(b, c).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "Argument `age: Int` added to `Football.skill`"
    assert diff[0].path == 'Football.skill'
    assert diff[0].criticality == Criticality.safe('Adding an optional argument is a safe change')


def test_field_type_change_is_safe():
    non_nullable_schema = schema("""
    type Query {
        a: Int!
    }
    """)
    nullable_schema = schema("""
    type Query {
        a: Int
    }
    """)
    # Dropping the non-null constraint is a breaking change because clients may have assumed it could never be null
    diff = Schema(non_nullable_schema, nullable_schema).diff()
    assert len(diff) == 1
    assert diff[0].criticality == Criticality.breaking(
        'Changing a field type will break queries that assume its type'
    )

    # But if it was already nullable, they already had to handle that case.
    diff = Schema(nullable_schema, non_nullable_schema).diff()
    assert len(diff) == 1
    assert diff[0].criticality == Criticality.safe()
