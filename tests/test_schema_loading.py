from pathlib import Path

from graphql import is_schema

from schemadiff.compare import Schema

TESTS_DATA = Path(__file__).parent / 'data'


def test_load_from_file():
    schema = Schema.from_file(TESTS_DATA / 'simple_schema.gql')
    assert is_schema(schema)
    assert len(schema.query_type.fields) == 2


def test_load_from_string():
    schema_string = """
    schema {
        query: Query
    }
    
    type Query {
        a: ID!
        b: MyType
    }
    
    type MyType {
        c: String
        d: Float
    }
    """
    schema = Schema.from_sdl(schema_string)
    assert is_schema(schema)
    assert len(schema.query_type.fields) == 2
