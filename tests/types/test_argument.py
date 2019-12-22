from graphql import build_schema as schema

from schemadiff.compare import SchemaComparator


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
    assert diff[0].message == (
        "Type for argument `arg1` on field `Math.sum` changed from `Int` to `Float`"
    )
    assert diff[0].path == 'Math.sum'


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
    assert diff[0].message == (
        "Argument `power: Int` added to `Field.exp`"
    )

    diff = SchemaComparator(b, a).compare()
    assert diff[0].message == (
        "Removed argument `power` from `Field.exp`"
    )


def test_argument_description_changed():
    a = schema('''
    input Precision {
        """result precision"""
        decimals: Int
    }
    type Math {
        sum(arg1: Precision): Float
    }
    ''')
    b = schema('''
    input Precision {
        """new desc"""
        decimals: Int
    }
    type Math {
        sum(arg1: Precision): Float
    }
    ''')

    diff = SchemaComparator(a, b).compare()
    assert len(diff) == 1
    assert diff[0].message == (
        "Description for Input field `Precision.decimals` "
        "changed from `result precision` to `new desc`"
    )


def test_argument_description_of_inner_type_changed():
    a = schema('''
    type TypeWithArgs {
      field(
        """abc"""
        a: Int
        b: String!
      ): String
    }
    ''')
    b = schema('''
    type TypeWithArgs {
      field(
        """zzz wxYZ"""
        a: Int
        b: String!
      ): String
    }
    ''')

    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 1
    assert diff[0].message == (
        "Description for argument `a` on field `TypeWithArgs.field` "
        "changed from `abc` to `zzz wxYZ`"
    )


def test_argument_default_value_changed():
    a = schema("""
    type Field {
        exp(base: Int=0): Int
    }
    """)
    b = schema("""
    type Field {
        exp(base: Int=1): Int
    }
    """)

    diff = SchemaComparator(a, b).compare()
    assert len(diff) == 1
    assert diff[0].message == (
        "Default value for argument `base` on field `Field.exp` changed from `0` to `1`"
    )
