from graphql import build_schema as schema

from schemadiff.compare import SchemaComparator


def test_enums_added_and_removed():
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
        C
        D
    }
    """)
    diff = SchemaComparator(a, b).compare()
    assert len(diff) == 3
    expected_diff = {
        "Enum value `B` was removed from `Letters` enum",
        "Enum value `C` was added to `Letters` enum",
        "Enum value `D` was added to `Letters` enum",
    }
    expected_paths = {'Letters.B', 'Letters.C', 'Letters.D'}
    for change in diff:
        assert change.message in expected_diff
        assert change.path in expected_paths


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
    diff = SchemaComparator(a, b).compare()
    assert len(diff) == 1
    assert diff[0].message == "Enum value `B` was deprecated with reason `Changed the alphabet`"
    assert diff[0].path == 'Letters.B'


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
    diff = SchemaComparator(a, b).compare()
    assert len(diff) == 1
    assert diff[0].message == (
        "Deprecation reason for enum value `B` changed from `a reason` to `a new reason`"
    )
    assert diff[0].path == 'Letters.B'


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
    diff = SchemaComparator(a, b).compare()
    assert len(diff) == 1
    assert diff[0].message == (
        "Description for enum value `A` set to `My new description`"
    )
    assert diff[0].path == 'Letters.A'


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
    diff = SchemaComparator(a, b).compare()
    assert len(diff) == 1
    assert diff[0].message == (
        "Description for enum value `A` changed from `My description` to `My new description`"
    )
    assert diff[0].path == 'Letters.A'
