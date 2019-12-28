from graphql import build_schema, GraphQLSchema as GQLSchema


class GraphQLSchema:
    """Represents a GraphQL Schema loaded from a string or file."""

    @classmethod
    def from_sdl(cls, schema_string: str) -> GQLSchema:
        return build_schema(schema_string)

    @classmethod
    def from_file(cls, filepath: str) -> GQLSchema:
        with open(filepath, encoding='utf-8') as f:
            schema_string = f.read()

        return cls.from_sdl(schema_string)
