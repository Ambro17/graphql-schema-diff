from graphql import build_schema as schema

from schemadiff.changes import CriticalityLevel, Criticality
from schemadiff.diff.schema import Schema

SAFE_CHANGE_MSG = "This change won't break any preexisting query"


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
    assert diff[0].criticality.level == CriticalityLevel.Breaking
    assert diff[0].criticality.reason == (
        "Changing the type of a field's argument can break existing queries that use this argument."
    )


def test_argument_add_non_nullable_field():
    a = schema("""
    type Field {
        exp(a: Int): Int
    }
    """)
    b = schema("""
    type Field {
        exp(a: Int, power: Int!): Int
    }
    """)
    diff = Schema(a, b).diff()
    assert len(diff) == 1
    change = diff[0]
    assert change.message == (
        "Argument `power: Int!` added to `Field.exp`"
    )
    assert change.path == 'Field.exp'
    assert change.criticality.level == CriticalityLevel.Breaking
    assert change.criticality.reason == (
        "Adding a required argument to an existing field is a "
        "breaking change because it will break existing uses of this field"
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

    diff = Schema(a, b).diff()
    assert len(diff) == 1
    assert diff[0].message == (
        "Argument `power: Int` added to `Field.exp`"
    )
    assert diff[0].path == 'Field.exp'
    assert diff[0].criticality.level == CriticalityLevel.NonBreaking
    assert diff[0].criticality.reason == "Adding an optional argument is a safe change"

    diff = Schema(b, a).diff()
    assert diff[0].message == (
        "Removed argument `power` from `Field.exp`"
    )
    assert diff[0].path == 'Field.exp'
    assert diff[0].criticality.level == CriticalityLevel.Breaking
    assert diff[0].criticality.reason == "Removing a field argument will break queries that use this argument"


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
    assert diff[0].criticality.level == CriticalityLevel.NonBreaking
    assert diff[0].criticality.reason == SAFE_CHANGE_MSG


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
    assert diff[0].criticality == Criticality.safe(SAFE_CHANGE_MSG)


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
    assert diff[0].criticality.level == CriticalityLevel.Dangerous
    assert diff[0].criticality.reason == (
        "Changing the default value for an argument may change the "
        "runtime behaviour of a field if it was never provided."
    )
