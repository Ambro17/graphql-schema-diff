from functools import partial

from graphql import (
    is_enum_type,
    is_union_type,
    is_input_object_type,
    is_object_type,
    is_interface_type,
)
from graphql.type.introspection import TypeFieldResolvers

from schemadiff.changes.directive import RemovedDirective, AddedDirective
from schemadiff.changes.type import (
    AddedType,
    RemovedType,
    TypeDescriptionChanged,
    TypeKindChanged,
)
from schemadiff.diff.directive import Directive
from schemadiff.diff.enum import EnumDiff
from schemadiff.diff.interface import InterfaceType
from schemadiff.diff.object_type import ObjectType
from schemadiff.diff.union_type import UnionType
from schemadiff.diff.input_object_type import InputObjectType

type_kind = partial(TypeFieldResolvers.kind, _info={})


class Schema:
    primitives = {'String', 'Int', 'Float', 'Boolean', 'ID'}
    internal_types = {'__Schema', '__Type', '__TypeKind', '__Field', '__InputValue', '__EnumValue',
                      '__Directive', '__DirectiveLocation'}

    def __init__(self, old_schema, new_schema):
        self.old_schema = old_schema
        self.new_schema = new_schema

        self.old_types = old_schema.type_map
        self.new_types = new_schema.type_map

        self.old_directives = old_schema.directives
        self.new_directives = new_schema.directives

    def diff(self):
        changes = []

        # Removed and added types
        changes += self.removed_types()
        changes += self.added_types()

        # Type changes for common types
        changes += self.common_type_changes()

        # Directive changes
        changes += self.directive_changes()

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
    def compare_types(old_type, new_type):
        changes = []
        if old_type.description != new_type.description:
            changes.append(TypeDescriptionChanged(new_type.name, old_type.description, new_type.description))

        if type_kind(old_type) != type_kind(new_type):
            changes.append(TypeKindChanged(new_type, type_kind(old_type), type_kind(new_type)))
        else:
            if is_enum_type(old_type):
                changes += EnumDiff(old_type, new_type).diff()
            elif is_union_type(old_type):
                changes += UnionType(old_type, new_type).diff()
            elif is_input_object_type(old_type):
                changes += InputObjectType(old_type, new_type).diff()
            elif is_object_type(old_type):
                changes += ObjectType(old_type, new_type).diff()
            elif is_interface_type(old_type):
                changes += InterfaceType(old_type, new_type).diff()

        return changes

    def directive_changes(self):
        changes = []
        changes += self.removed_directives()
        changes += self.added_directives()
        changes += self.common_directives_changes()
        return changes

    def removed_directives(self):
        new_directive_names = {x.name for x in self.new_directives}
        return [
            RemovedDirective(directive)
            for directive in self.old_directives
            if directive.name not in new_directive_names
        ]

    def added_directives(self):
        old_directive_names = {x.name for x in self.old_directives}
        return [
            AddedDirective(directive, directive.locations)
            for directive in self.new_directives
            if directive.name not in old_directive_names
        ]

    def common_directives_changes(self):
        old_directive_names = {x.name for x in self.old_directives}
        new_directive_names = {x.name for x in self.new_directives}
        old_directives = {
            x.name: x
            for x in self.old_directives
        }
        new_directives = {
            x.name: x
            for x in self.new_directives
        }

        changes = []
        for directive_name in old_directive_names & new_directive_names:
            changes += Directive(old_directives[directive_name], new_directives[directive_name]).diff()

        return changes

    def is_primitive(self, atype):
        return atype in self.primitives
