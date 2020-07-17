from graphql import build_schema, GraphQLSchema


class SchemaLoader:
    """Represents a GraphQL Schema loaded from a string or file."""

    @classmethod
    def from_sdl(cls, schema_string: str) -> GraphQLSchema:
        return build_schema(schema_string)

    @classmethod
    def from_file(cls, filepath: str) -> GraphQLSchema:
        with open(filepath, encoding='utf-8') as f:
            schema_string = f.read()

        return cls.from_sdl(schema_string)
