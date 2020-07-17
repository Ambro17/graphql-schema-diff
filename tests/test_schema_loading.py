from pathlib import Path

import pytest
from graphql import is_schema, GraphQLSyntaxError

from schemadiff import diff, diff_from_file
from schemadiff.schema_loader import SchemaLoader

TESTS_DATA = Path(__file__).parent / 'data'


def test_load_from_file():
    schema = SchemaLoader.from_file(TESTS_DATA / 'simple_schema.gql')
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
    schema = SchemaLoader.from_sdl(schema_string)
    assert is_schema(schema)
    assert len(schema.query_type.fields) == 2


def test_diff_from_str():
    schema_str = """
    schema {
        query: Query
    }
    type Query {
        a: ID!
        b: Int
    }
    """
    changes = diff(schema_str, schema_str)
    assert changes == []


def test_diff_from_schema():
    schema_object = SchemaLoader.from_sdl("""
    schema {
        query: Query
    }
    type Query {
        a: ID!
        b: Int
    }
    """)
    assert is_schema(schema_object)
    changes = diff(schema_object, schema_object)
    assert changes == []


def test_diff_from_file():
    changes = diff_from_file(TESTS_DATA / 'simple_schema.gql', TESTS_DATA / 'simple_schema_dangerous_changes.gql')
    assert changes
    assert len(changes) == 2


def test_load_invalid_schema():
    with pytest.raises(TypeError, match="Unknown type 'InvalidType'"):
        SchemaLoader.from_file(TESTS_DATA / 'invalid_schema.gql')


@pytest.mark.parametrize("schema", ["", "{}", "\n{}\n", "[]"])
def test_load_empty_schema(schema):
    with pytest.raises(GraphQLSyntaxError):
        SchemaLoader.from_sdl(schema)
