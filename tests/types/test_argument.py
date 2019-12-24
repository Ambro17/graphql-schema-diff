from graphql import build_schema as schema

from schemadiff.diff.schema import Schema


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

    diff = Schema(a, b).diff()
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

    diff = Schema(a, b).diff()
    assert len(diff) == 1
    assert diff[0].message == (
        "Argument `power: Int` added to `Field.exp`"
    )
    assert diff[0].path == 'Field.exp'

    diff = Schema(b, a).diff()
    assert diff[0].message == (
        "Removed argument `power` from `Field.exp`"
    )
    assert diff[0].path == 'Field.exp'


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

    diff = Schema(a, b).diff()
    assert len(diff) == 1
    assert diff[0].message == (
        "Description for Input field `Precision.decimals` "
        "changed from `result precision` to `new desc`"
    )
    assert diff[0].path == 'Precision.decimals'


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

    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == (
        "Description for argument `a` on field `TypeWithArgs.field` "
        "changed from `abc` to `zzz wxYZ`"
    )
    assert diff[0].path == 'TypeWithArgs.field'


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

    diff = Schema(a, b).diff()
    assert len(diff) == 1
    assert diff[0].message == (
        "Default value for argument `base` on field `Field.exp` changed from `0` to `1`"
    )
    assert diff[0].path == 'Field.exp'
