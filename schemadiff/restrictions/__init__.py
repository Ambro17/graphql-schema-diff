from abc import ABC
from typing import List, Set

from schemadiff.changes.type import TypeDescriptionChanged, AddedType


class Restriction(ABC):
    """Metaclass for creating schema restrictions."""
    name: str = ""

    @classmethod
    def is_restricted(cls, change) -> bool:
        """Evaluate the change regarding the restriction
        class defined.

        Returns:
            bool: True if restricted, False otherwise
        """
        raise NotImplemented(f"Restriction {cls.__name__!r} should implement the `is_restricted` method")

    @classmethod
    def get_subclasses_by_names(cls, names: List[str]) -> Set:
        if not names:
            return set()
        return {subclass for subclass in cls.__subclasses__() if subclass.name in names}

    @classmethod
    def get_restrictions_list(cls) -> Set[str]:
        return {subclass.name for subclass in cls.__subclasses__()}


class RestrictAddingWithoutDescription(Restriction):
    """Restrict adding new GraphQL types without entering
    a non-empty description."""
    name = "add-type-without-description"

    @classmethod
    def is_restricted(cls, change) -> bool:
        if isinstance(change, AddedType):
            return change.type.description in (None, "")
        return False


class RestrictRemovingDescription(Restriction):
    """Restrict removing the description from an existing
    GraphQL type."""
    name = "remove-type-description"

    @classmethod
    def is_restricted(cls, change) -> bool:
        if isinstance(change, TypeDescriptionChanged):
            return change.new_desc in (None, "")
        return False
