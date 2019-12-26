from graphql import build_schema as schema

from schemadiff.changes import Criticality
from schemadiff.diff.schema import Schema


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
    diff = Schema(two_types, three_types).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "Union member `Unknown` was added to `Outcome` Union type"
    assert diff[0].path == 'Outcome'
    assert diff[0].criticality == Criticality.dangerous(
        'Adding a possible type to Unions may break existing clients '
        'that were not programming defensively against a new possible type.'
    )

    diff = Schema(three_types, two_types).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "Union member `Unknown` was removed from `Outcome` Union type"
    assert diff[0].path == 'Outcome'
    assert diff[0].criticality == Criticality.breaking(
        'Removing a union member from a union can break queries that use this union member in a fragment spread'
    )
