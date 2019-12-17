from graphql import build_schema as schema

from diff.compare import SchemaComparator

"""
assert "Type for argument `foo` on field `Query.a` changed from `String` to `Boolean`"
assert "Type for argument `arg` on field `Query.a` changed from `[String]` to `String`"
assert "Type for argument `arg` on field `Query.a` changed from `String!` to `String`"
assert "Type for argument `arg` on field `Query.a` changed from `String` to `String!`"
assert "Type for argument `arg` on field `Query.a` changed from `[String]!` to `[String]`"
assert "Type for argument `arg` on field `Query.a` changed from `[String!]!` to `[String]!`"
assert "Type for argument `arg` on field `Query.a` changed from `[String!]!` to `[String]`"
assert "Type for argument `arg` on field `Query.a` changed from `[String!]!` to `[Boolean]`"
"""


def test_argument_type_changed():
    a = schema("""
    type Math {
        sum(arg1: Int, arg2: Int): Int
    }
    """)
    b = schema("""
    type Math {
        sum(arg1: Float, arg2: Int): Int
    }
    """)

    diff = SchemaComparator(a, b).compare()
    assert len(diff) == 1
    assert diff[0].message() == (
        "Type for argument 'arg1' on field 'Math.sum' changed from 'Int' to 'Float'"
    )


def test_argument_added_removed():
    a = schema("""
    type Field {
        exp(a: Int): Int
    }
    """)
    b = schema("""
    type Field {
        exp(a: Int, power: Int): Int
    }
    """)

    diff = SchemaComparator(a, b).compare()
    assert len(diff) == 1
    assert diff[0].message() == (
        "Added argument 'power' in 'Field.exp' with type Int"
    )

    diff = SchemaComparator(b, a).compare()
    assert diff[0].message() == (
        "Removed argument 'power' from 'Field.exp'"
    )
