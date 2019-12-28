from pathlib import Path

import pytest
from graphql import is_schema, GraphQLSyntaxError

from schemadiff.graphql_schema import GraphQLSchema

TESTS_DATA = Path(__file__).parent / 'data'


def test_load_from_file():
    schema = GraphQLSchema.from_file(TESTS_DATA / 'simple_schema.gql')
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
    schema = GraphQLSchema.from_sdl(schema_string)
    assert is_schema(schema)
    assert len(schema.query_type.fields) == 2


def test_load_invalid_schema():
    with pytest.raises(TypeError, match="Unknown type 'InvalidType'"):
        GraphQLSchema.from_file(TESTS_DATA / 'invalid_schema.gql')


@pytest.mark.parametrize("schema", ["", "{}", "\n{}\n", "[]"])
def test_load_empty_schema(schema):
    with pytest.raises(GraphQLSyntaxError):
        GraphQLSchema.from_sdl(schema)
