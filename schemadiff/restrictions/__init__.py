from abc import ABC, abstractmethod
from typing import List, Set

from schemadiff.changes.enum import EnumValueAdded, EnumValueDescriptionChanged
from schemadiff.changes.object import ObjectTypeFieldAdded
from schemadiff.changes.type import AddedType, TypeDescriptionChanged

class Restriction(ABC):
    """Metaclass for creating schema restrictions."""
    name: str = ""

    @classmethod
    @abstractmethod
    def is_restricted(cls, change) -> bool:
        """Evaluate the change regarding the restriction
        class defined.

        Returns:
            bool: True if restricted, False otherwise
        """

    @classmethod
    def get_subclasses_by_names(cls, names: List[str]) -> Set:
        if not names:
            return set()
        return {subclass for subclass in cls.__subclasses__() if subclass.name in names}

    @classmethod
    def get_restrictions_list(cls) -> Set[str]:
        return {subclass.name for subclass in cls.__subclasses__()}


class RestrictAddingTypeWithoutDescription(Restriction):
    """Restrict adding new GraphQL types without entering
    a non-empty description."""
    name = "add-type-without-description"

    @classmethod
    def is_restricted(cls, change) -> bool:
        if isinstance(change, AddedType):
            return change.type.description in (None, "")
        return False


class RestrictRemovingTypeDescription(Restriction):
    """Restrict removing the description from an existing
    GraphQL type."""
    name = "remove-type-description"

    @classmethod
    def is_restricted(cls, change) -> bool:
        if isinstance(change, TypeDescriptionChanged):
            return change.new_desc in (None, "")
        return False


class RestrictAddingFieldsWithoutDescription(Restriction):
    """Restrict adding fields without description."""
    name = "add-field-without-description"

    @classmethod
    def is_restricted(cls, change) -> bool:
        if isinstance(change, ObjectTypeFieldAdded):
            return change.description in (None, "")
        return False


class RestrictAddingEnumWithoutDescription(Restriction):
    """Restrict adding enum value without description."""
    name = "add-enum-value-without-description"

    @classmethod
    def is_restricted(cls, change) -> bool:
        if isinstance(change, EnumValueAdded):
            return change.description in (None, "")
        return False


class RestrictRemovingEnumValueDescription(Restriction):
    """Restrict adding enum value without description."""
    name = "remove-enum-value-description"

    @classmethod
    def is_restricted(cls, change) -> bool:
        if isinstance(change, EnumValueDescriptionChanged):
            return change.new_value.description in (None, "")
        return False
