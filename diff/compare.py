from graphql import (
    is_enum_type,
    is_union_type,
    is_input_object_type,
    is_object_type,
    is_interface_type,
)

from changes import (
    SchemaQueryChange,
    RemovedType,
    AddedType,
)
from diff.types.enum import EnumDiff
from diff.types.object_type import ObjectType


class SchemaComparator:
    primitives = {'String', 'Int', 'Float', 'Boolean', 'ID'}
    internal_types = {'__Schema', '__Type', '__TypeKind', '__Field', '__InputValue', '__EnumValue',
                      '__Directive', '__DirectiveLocation'}

    def __init__(self, old_schema, new_schema):
        if None in (old_schema.query_type, new_schema.query_type):
            raise ValueError("Invalid schema. Query object must be defined.")

        self.old_schema = old_schema
        self.new_schema = new_schema

        self.old_query_fields = self.old_schema.query_type.fields
        self.new_query_fields = self.new_schema.query_type.fields

        self.old_types = old_schema.type_map
        self.new_types = new_schema.type_map

        self.old_directives = old_schema.directives
        self.new_directives = new_schema.directives

    def compare(self):
        changes = []
        # Removed and added types
        changes += self.removed_types()
        changes += self.added_types()

        # Type diff for common types
        changes += self.common_type_changes()

        # Schema and directive changes
        # changes += self.schema_changes()
        # changes += self.directive_changes()

        return changes

    def removed_types(self):
        return [
            RemovedType(self.old_types[field_name])
            for field_name in self.old_types
            if field_name not in self.new_types and not self.is_primitive(field_name)
        ]

    def added_types(self):
        return [
            AddedType(self.new_types[field_name])
            for field_name in self.new_types
            if field_name not in self.old_types and not self.is_primitive(field_name)
        ]

    def common_type_changes(self):
        changes = []

        common_types = (set(self.old_types.keys()) & set(self.new_types.keys())) - self.primitives - self.internal_types
        for type_name in common_types:
            old_type = self.old_types[type_name]
            new_type = self.new_types[type_name]
            changes += self.compare_types(old_type, new_type)

        return changes

    @staticmethod
    def compare_types(old, new):
        changes = []
        if old.description != new.description:
            changes.append((old.description, new.description))
        if type(old) != type(new):
            changes.append((old, new))
        else:
            if is_enum_type(old):
                changes += EnumDiff(old, new)()
            elif is_union_type(old):
                pass
            elif is_input_object_type(old):
                pass
            elif is_object_type(old):
                changes += ObjectType(old, new).diff()
                assert 1
                assert 2
            elif is_interface_type(old):
                pass

        return changes

    def schema_changes(self):
        changes = []
        oldq = self.old_schema.query_type
        newq = self.new_schema.query_type
        if oldq != newq:
            changes.append(SchemaQueryChange(oldq, newq))

        if self.old_schema.mutation_type != self.new_schema.mutation_type:
            changes.append((self.old_schema, self.new_schema))

        if self.old_schema.subscription_type != self.new_schema.subscription_type:
            changes.append((self.old_schema, self.new_schema))

        return changes

    def directive_changes(self):
        changes = []
        changes += self.removed_directives()
        changes += self.added_directives()
        changes += self.common_directives_changes()
        return changes

    def removed_directives(self):
        return [
            x
            for x in self.old_directives
            if x not in self.new_directives
        ]

    def added_directives(self):
        return [
            x
            for x in self.new_directives
            if x not in self.old_directives
        ]

    def common_directives_changes(self):
        changes = []
        directives = (x.name for x in self.old_directives if x.name in self.new_directives)
        for directive in directives:
            old_directive = self.old_directives[directive.name]
            new_directive = self.new_directives[directive.name]
            changes += self.compare_directives(old_directive, new_directive)

        return changes

    def compare_directives(self, x, y):
        return []

    def is_primitive(self, atype):
        return atype in self.primitives


class Schema:
    """Represents a GraphQL Schema loaded from a string or file."""

    def __init__(self):
        pass

    @classmethod
    def from_sdl(cls):
        return cls()

    @classmethod
    def from_file(cls):
        return cls()

    def __eq__(self, other):
        return False
