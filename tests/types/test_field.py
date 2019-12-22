from graphql import build_schema as schema
from diff.compare import SchemaComparator


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
    diff = SchemaComparator(a, b).compare()
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
    diff = SchemaComparator(a_schema, changed_schema).compare()
    assert len(diff) == 1
    expected_diff = ["Field `Query.a` changed type from `String!` to `Int`"]
    assert [x.message() for x in diff] == expected_diff


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
    diff = SchemaComparator(a, b).compare()
    assert len(diff) == 1
    expected_diff = ["Field `Query.a` changed type from `String` to `[String]`"]
    assert [x.message() for x in diff] == expected_diff


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
    diff = SchemaComparator(a, b).compare()
    assert len(diff) == 1
    expected_diff = ["Field `Query.a` changed type from `Int!` to `Int`"]
    assert [x.message() for x in diff] == expected_diff

    diff = SchemaComparator(b, a).compare()
    assert len(diff) == 1
    expected_diff = ["Field `Query.a` changed type from `Int` to `Int!`"]
    assert [x.message() for x in diff] == expected_diff


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
    diff = SchemaComparator(a, b).compare()
    assert len(diff) == 1
    expected_diff = ["Field `Query.a` changed type from `[Boolean]!` to `[Boolean]`"]
    assert [x.message() for x in diff] == expected_diff


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
    diff = SchemaComparator(a, b).compare()
    assert len(diff) == 1
    expected_diff = ["Field `Query.a` changed type from `[Int!]!` to `[Int]!`"]
    assert [x.message() for x in diff] == expected_diff


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
    diff = SchemaComparator(a, b).compare()
    assert len(diff) == 1
    expected_diff = ["Field `Query.a` changed type from `[Float!]!` to `[Float]`"]
    assert [x.message() for x in diff] == expected_diff


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
    diff = SchemaComparator(a, b).compare()
    assert len(diff) == 1
    expected_diff = ["Field `Query.a` changed type from `[Float!]!` to `[String]`"]
    assert [x.message() for x in diff] == expected_diff


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
    diff = SchemaComparator(a, b).compare()
    assert len(diff) == 1
    expected_diff = ["Field `Query.a` description changed from `some desc` to `once upon a time`"]
    assert [x.message() for x in diff] == expected_diff


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
    diff = SchemaComparator(a, b).compare()
    assert len(diff) == 1
    expected_diff = ["Deprecation reason on field `Query.b` changed from `Not used` to `Some string`"]
    assert [x.message() for x in diff] == expected_diff


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
    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "Argument `player: ID` added to `Football.skill`"

    diff = SchemaComparator(b, a).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "Removed argument `player` from `Football.skill`"

    c = schema("""
    type Football {
        skill(player: ID, age: Int): Float!
    }
    """)
    diff = SchemaComparator(b, c).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "Argument `age: Int` added to `Football.skill`"
