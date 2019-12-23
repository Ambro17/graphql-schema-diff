from graphql import build_schema as schema

from schemadiff.compare import SchemaComparator


def test_add_type_to_union():
    two_types = schema("""
    type Query {
        c: Int
    }
    type Result {
        message: String
    }
    type Error {
        message: String
        details: String
    }
        type Unknown {
        message: String
        details: String
        traceback: String
    }

    union Outcome = Result | Error
    """)

    three_types = schema("""
    type Query {
        c: Int
    }
    type Result {
        message: String
    }
    type Error {
        message: String
        details: String
    }
    type Unknown {
        message: String
        details: String
        traceback: String
    }

    union Outcome = Result | Error | Unknown
    """)
    diff = SchemaComparator(two_types, three_types).compare()
    assert diff and len(diff) == 1
    assert diff[0].message == "Union member `Unknown` was added to `Outcome` Union type"
    assert diff[0].path == 'Outcome'

    diff = SchemaComparator(three_types, two_types).compare()
    assert diff and len(diff) == 1
    assert diff[0].message == "Union member `Unknown` was removed from `Outcome` Union type"
    assert diff[0].path == 'Outcome'
