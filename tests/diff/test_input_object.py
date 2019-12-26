from graphql import build_schema as schema

from schemadiff.changes import Criticality
from schemadiff.diff.schema import Schema

ERROR = 'Changing the type of an input field can break existing queries that use this field'


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
    diff = Schema(a, b).diff()
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
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "`Params.love` type changed from `Int` to `Float!`"
    assert diff[0].path == 'Params.love'
    assert diff[0].criticality == Criticality.breaking(
        'Changing the type of an input field can break existing queries that use this field'
    )


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
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "`Params.arg` type changed from `Int` to `[Int]`"
    assert diff[0].path == 'Params.arg'
    assert diff[0].criticality == Criticality.breaking(
        'Changing the type of an input field can break existing queries that use this field'
    )


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
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "`Params.arg` type changed from `String!` to `String`"
    assert diff[0].path == 'Params.arg'
    assert diff[0].criticality == Criticality.safe()


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
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "`Params.arg` type changed from `ID` to `ID!`"
    assert diff[0].path == 'Params.arg'
    assert diff[0].criticality == Criticality.breaking(ERROR)


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
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "`Params.arg` type changed from `[ID!]!` to `[ID!]`"
    assert diff[0].path == 'Params.arg'
    assert diff[0].criticality == Criticality.safe()  # Because dropping the non-null constraint will not break anything

    diff = Schema(a, c).diff()
    assert diff[0].message == "`Params.arg` type changed from `[ID!]!` to `[ID]`"
    assert diff[0].path == 'Params.arg'
    assert diff[0].criticality == Criticality.breaking(ERROR)

    diff = Schema(a, d).diff()
    assert diff[0].message == "`Params.arg` type changed from `[ID!]!` to `ID`"
    assert diff[0].path == 'Params.arg'
    assert diff[0].criticality == Criticality.breaking(ERROR)


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
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "`Params.arg` type changed from `[Int]` to `[String]`"
    assert diff[0].path == 'Params.arg'
    assert diff[0].criticality == Criticality.breaking(ERROR)


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
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "Default value for input field `Params.love` changed from `0` to `100`"
    assert diff[0].path == 'Params.love'
    assert diff[0].criticality == Criticality.dangerous(
        'Changing the default value for an argument may change '
        'the runtime behaviour of a field if it was never provided.'
    )


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
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == (
        "Description for Input field `Params.love` changed from `abc` to `His description`"
    )
    assert diff[0].path == 'Params.love'
    assert diff[0].criticality == Criticality.safe()


def test_input_field_added_field():
    a = schema("""
    input Recipe {
        ingredients: [String]
    }
    """)
    b = schema("""
    input Recipe {
        ingredients: [String]
        love: Float
    }
    """)
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == (
        "Input Field `love: Float` was added to input type `Recipe`"
    )
    assert diff[0].path == 'Recipe.love'
    assert diff[0].criticality == Criticality.safe()

    diff = Schema(b, a).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == (
        "Input Field `love` removed from input type `Recipe`"
    )
    assert diff[0].path == 'Recipe.love'
    assert diff[0].criticality == Criticality.breaking(
        'Removing an input field will break queries that use this input field.'
    )


def test_add_non_null_input_field():
    a = schema("""
    input Recipe {
        ingredients: [String]
    }
    """)
    b = schema("""
    input Recipe {
        ingredients: [String]
        love: Float!
    }
    """)
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == (
        "Input Field `love: Float!` was added to input type `Recipe`"
    )
    assert diff[0].path == 'Recipe.love'
    assert diff[0].criticality == Criticality.breaking(
        'Adding a non-null field to an existing input type will cause existing '
        'queries that use this input type to break because they will not provide a value for this new field.'
    )
