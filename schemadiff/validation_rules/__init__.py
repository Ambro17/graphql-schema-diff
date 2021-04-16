import typing
from abc import ABC, abstractmethod
from typing import List, Set

from graphql import GraphQLObjectType

from schemadiff.changes.enum import EnumValueAdded, EnumValueDescriptionChanged
from schemadiff.changes.field import FieldDescriptionChanged, FieldArgumentAdded
from schemadiff.changes.object import ObjectTypeFieldAdded
from schemadiff.changes.type import AddedType, TypeDescriptionChanged


class ValidationRule(ABC):
    """Abstract class for creating schema Validation Rules."""
    name: str = ""

    def __init__(self, change):
        self.change = change

    @abstractmethod
    def is_valid(self) -> bool:
        """Evaluate the change regarding the rule class defined.

        Returns:
            bool: True if change is valid, False otherwise
        """

    @property
    @abstractmethod
    def message(self) -> str:
        """Formatted change message"""

    @classmethod
    def get_subclasses_by_names(cls, names: List[str]) -> Set[typing.Type['ValidationRule']]:
        if not names:
            return set()
        return {subclass for subclass in cls.__subclasses__() if subclass.name in names}

    @classmethod
    def get_rules_list(cls) -> Set[str]:
        return {subclass.name for subclass in cls.__subclasses__()}


class AddTypeWithoutDescription(ValidationRule):
    """Restrict adding new GraphQL types without entering
    a non-empty description."""
    name = "add-type-without-description"

    def is_valid(self) -> bool:
        EMPTY = (None, "")
        if not isinstance(self.change, AddedType):
            return True

        added_type = self.change.type
        type_has_description = added_type.description not in EMPTY

        if isinstance(added_type, GraphQLObjectType):
            all_its_fields_have_description = all(
                field.description not in EMPTY
                for field in added_type.fields.values()
            )
            return type_has_description and all_its_fields_have_description
        else:
            return type_has_description

    @property
    def message(self):
        return f"{self.change.message} without a description for {self.change.path} (rule: `{self.name}`)."


class RemoveTypeDescription(ValidationRule):
    """Restrict removing the description from an existing
    GraphQL type."""
    name = "remove-type-description"

    def is_valid(self) -> bool:
        if isinstance(self.change, TypeDescriptionChanged):
            return self.change.new_desc not in (None, "")
        return True

    @property
    def message(self):
        return (
            f"Description for type `{self.change.type}` was "
            f"removed (rule: `{self.name}`)"
        )


class AddFieldWithoutDescription(ValidationRule):
    """Restrict adding fields without description."""
    name = "add-field-without-description"

    def is_valid(self) -> bool:
        if isinstance(self.change, ObjectTypeFieldAdded):
            return self.change.description not in (None, "")
        return True

    @property
    def message(self):
        return f"{self.change.message} without a description for {self.change.path} (rule: `{self.name}`)."


class RemoveFieldDescription(ValidationRule):
    """Restrict removing field description."""
    name = "remove-field-description"

    def is_valid(self) -> bool:
        if isinstance(self.change, FieldDescriptionChanged):
            return self.change.new_field.description not in (None, "")
        return True

    @property
    def message(self):
        return (
            f"`{self.change.type.name}.{self.change.field_name}` description was "
            f"removed (rule: `{self.name}`)"
        )


class AddEnumValueWithoutDescription(ValidationRule):
    """Restrict adding enum value without description."""
    name = "add-enum-value-without-description"

    def is_valid(self) -> bool:
        if isinstance(self.change, EnumValueAdded):
            return self.change.description not in (None, "")
        return True

    @property
    def message(self):
        return f"{self.change.message} without a description (rule: `{self.name}`)"


class RemoveEnumValueDescription(ValidationRule):
    """Restrict adding enum value without description."""
    name = "remove-enum-value-description"

    def is_valid(self) -> bool:
        if isinstance(self.change, EnumValueDescriptionChanged):
            return self.change.new_value.description not in (None, "")
        return True

    @property
    def message(self):
        return f"Description for enum value `{self.change.name}` was removed (rule: `{self.name}`)"


