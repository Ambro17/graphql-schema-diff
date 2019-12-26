from graphql import build_schema as schema

from schemadiff.changes import Criticality
from schemadiff.diff.schema import Schema


def test_enum_value_removed():
    a = schema("""
    type Query {
        a: String
    }
    enum Letters {
        A
        B
    }
    """)
    b = schema("""
    type Query {
        a: String
    }
    enum Letters {
        A
    }
    """)
    diff = Schema(a, b).diff()
    assert len(diff) == 1
    change = diff[0]
    assert change.message == "Enum value `B` was removed from `Letters` enum"
    assert change.path == 'Letters'
    assert change.criticality == Criticality.breaking(
        'Removing an enum value will break existing queries that use this enum value'
    )


def test_enums_added():
    a = schema("""
    type Query {
        a: String
    }
    enum Letters {
        A
        B
    }
    """)
    b = schema("""
    type Query {
        a: String
    }
    enum Letters {
        A
        B
        C
        D
    }
    """)
    diff = Schema(a, b).diff()
    assert len(diff) == 2
    expected_diff = {
        "Enum value `C` was added to `Letters` enum",
        "Enum value `D` was added to `Letters` enum",
    }
    expected_paths = {'Letters.C', 'Letters.D'}
    for change in diff:
        assert change.message in expected_diff
        assert change.path in expected_paths
        assert change.criticality == Criticality.dangerous(
            "Adding an enum value may break existing clients that "
            "were not programming defensively against an added case when querying an enum."
        )


def test_deprecated_enum_value():
    a = schema("""
    type Query {
        a: Int
    }
    enum Letters {
        A
        B
    }
    """)
    b = schema("""
    type Query {
        a: Int
    }
    enum Letters {
        A
        B @deprecated(reason: "Changed the alphabet")
    }
    """)
    diff = Schema(a, b).diff()
    assert len(diff) == 1
    assert diff[0].message == "Enum value `B` was deprecated with reason `Changed the alphabet`"
    assert diff[0].path == 'Letters.B'
    assert diff[0].criticality == Criticality.safe(
        "A deprecated field can still be used by clients and will give them time to adapt their queries"
    )


def test_deprecated_reason_changed():
    a = schema("""
    type Query {
        a: Int
    }
    enum Letters {
        A
        B @deprecated(reason: "a reason")
    }
    """)
    b = schema("""
    type Query {
        a: Int
    }
    enum Letters {
        A
        B @deprecated(reason: "a new reason")
    }
    """)
    diff = Schema(a, b).diff()
    assert len(diff) == 1
    assert diff[0].message == (
        "Deprecation reason for enum value `B` changed from `a reason` to `a new reason`"
    )
    assert diff[0].path == 'Letters.B'
    assert diff[0].criticality == Criticality.safe(
        "A deprecated field can still be used by clients and will give them time to adapt their queries"
    )


def test_description_added():
    a = schema('''
    type Query {
        a: Int
    }
    enum Letters {
        A
    }
    ''')
    b = schema('''
    type Query {
        a: Int
    }
    enum Letters {
        """My new description"""
        A
    }
    ''')
    diff = Schema(a, b).diff()
    assert len(diff) == 1
    assert diff[0].message == (
        "Description for enum value `A` set to `My new description`"
    )
    assert diff[0].path == 'Letters.A'
    assert diff[0].criticality == Criticality.safe()


def test_description_changed():
    a = schema('''
    type Query {
        a: Int
    }
    enum Letters {
        """My description"""
        A
    }
    ''')
    b = schema('''
    type Query {
        a: Int
    }
    enum Letters {
        """My new description"""
        A
    }
    ''')
    diff = Schema(a, b).diff()
    assert len(diff) == 1
    assert diff[0].message == (
        "Description for enum value `A` changed from `My description` to `My new description`"
    )
    assert diff[0].path == 'Letters.A'
    assert diff[0].criticality == Criticality.safe()
