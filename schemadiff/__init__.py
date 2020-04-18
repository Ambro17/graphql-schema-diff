from typing import Union

from graphql import GraphQLSchema as GQLSchema, is_schema

from schemadiff.changes import Change
from schemadiff.diff.schema import Schema
from schemadiff.graphql_schema import GraphQLSchema
from schemadiff.formatting import print_diff, format_diff


def diff(schema_a: Union[str, GQLSchema], schema_b: Union[str, GQLSchema]) -> [Change]:
    """Compare two graphql schemas SDLs highlighting dangerous and breaking changes.

    Returns:
        changes (list<Change>): List of differences between both schemas with details about each change
    """
    first = GraphQLSchema.from_sdl(schema_a) if not is_schema(schema_a) else schema_a
    second = GraphQLSchema.from_sdl(schema_b) if not is_schema(schema_b) else schema_b
    return Schema(first, second).diff()


def diff_from_file(schema_file: str, other_schema_file: str):
    """Compare two graphql schema files highlighting dangerous and breaking changes.

    Returns:
        changes (list<Change>): List of differences between both schemas with details about each change
    """
    first = GraphQLSchema.from_file(schema_file)
    second = GraphQLSchema.from_file(other_schema_file)
    return Schema(first, second).diff()


__all__ = [
    'diff',
    'diff_from_file',
    'format_diff',
    'print_diff',
]
