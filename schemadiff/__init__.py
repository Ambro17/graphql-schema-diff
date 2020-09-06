from typing import Union, List

from graphql import GraphQLSchema as GQLSchema, is_schema

from schemadiff.changes import Change
from schemadiff.diff.schema import Schema
from schemadiff.schema_loader import SchemaLoader
from schemadiff.formatting import print_diff, format_diff
from schemadiff.validation import validate_diff


SDL = str  # Alias for string describing schema through schema definition language


def diff(old_schema: Union[SDL, GQLSchema], new_schema: Union[SDL, GQLSchema]) -> List[Change]:
    """Compare two graphql schemas highlighting dangerous and breaking changes.

    Returns:
        changes (List[Change]): List of differences between both schemas with details about each change
    """
    first = SchemaLoader.from_sdl(old_schema) if not is_schema(old_schema) else old_schema
    second = SchemaLoader.from_sdl(new_schema) if not is_schema(new_schema) else new_schema
    return Schema(first, second).diff()


def diff_from_file(schema_file: str, other_schema_file: str):
    """Compare two graphql schema files highlighting dangerous and breaking changes.

    Returns:
        changes (List[Change]): List of differences between both schemas with details about each change
    """
    first = SchemaLoader.from_file(schema_file)
    second = SchemaLoader.from_file(other_schema_file)
    return Schema(first, second).diff()


__all__ = [
    'diff',
    'diff_from_file',
    'format_diff',
    'print_diff',
    'validate_diff',
    'Change',
]
