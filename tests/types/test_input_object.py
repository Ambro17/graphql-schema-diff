from graphql import build_schema as schema
from diff.compare import SchemaComparator


def test_input_field_no_diff():
    a = schema("""
    input Params {
        will: String!
        love: Int!
    }
    """)
    b = schema("""
    input Params {
        will: String!
        love: Int!
    }
    """)
    diff = SchemaComparator(a, b).compare()
    assert not diff


def test_input_field_type_changed():
    a = schema("""
    input Params {
        will: String!
        love: Int
    }
    """)
    b = schema("""
    input Params {
        will: String!
        love: Float!
    }
    """)
    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "'Params.love' type changed from 'Int' to 'Float!'"


def test_input_field_changed_from_list_to_scalar():
    a = schema("""
    input Params {
        arg: Int
    }
    """)
    b = schema("""
    input Params {
        arg: [Int]
    }
    """)
    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "'Params.arg' type changed from 'Int' to '[Int]'"


def test_input_field_dropped_non_null_constraint():
    a = schema("""
    input Params {
        arg: String!
    }
    """)
    b = schema("""
    input Params {
        arg: String
    }
    """)
    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "'Params.arg' type changed from 'String!' to 'String'"


def test_input_field_now_is_not_nullable():
    a = schema("""
    input Params {
        arg: ID
    }
    """)
    b = schema("""
    input Params {
        arg: ID!
    }
    """)
    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "'Params.arg' type changed from 'ID' to 'ID!'"


def test_input_field_type_nullability_change_on_lists_of_the_same_underlying_types():
    a = schema("""
    input Params {
        arg: [ID!]!
    }
    """)
    b = schema("""
    input Params {
        arg: [ID!]
    }
    """)
    c = schema("""
    input Params {
        arg: [ID]
    }
    """)
    d = schema("""
    input Params {
        arg: ID
    }
    """)
    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "'Params.arg' type changed from '[ID!]!' to '[ID!]'"

    diff = SchemaComparator(a, c).compare()
    assert diff[0].message() == "'Params.arg' type changed from '[ID!]!' to '[ID]'"

    diff = SchemaComparator(a, d).compare()
    assert diff[0].message() == "'Params.arg' type changed from '[ID!]!' to 'ID'"


def test_input_field_inner_type_changed():
    a = schema("""
    input Params {
        arg: [Int]
    }
    """)
    b = schema("""
    input Params {
        arg: [String]
    }
    """)
    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "'Params.arg' type changed from '[Int]' to '[String]'"


def test_input_field_default_value_changed():
    a = schema("""
    input Params {
        love: Int = 0
    }
    """)
    b = schema("""
    input Params {
        love: Int = 100
    }
    """)
    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "Default value for Input field 'Params.love' changed from 0 to 100"


def test_input_field_description_changed():
    a = schema('''
    input Params {
        """abc"""
        love: Int
    }
    ''')
    b = schema('''
    input Params {
        """His description"""
        love: Int
    }
    ''')
    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == (
        "Description for Input field 'Params.love' changed from 'abc' to 'His description'"
    )
