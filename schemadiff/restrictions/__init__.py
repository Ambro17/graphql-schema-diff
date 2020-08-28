from abc import ABC
from typing import List

from schemadiff.changes.type import TypeDescriptionChanged, AddedType


class Restriction(ABC):
    """Metaclass for creating schema restrictions."""
    reason: str = ""

    @classmethod
    def is_restricted(cls, change) -> bool:
        """Evaluate the change regarding the restriction
        class defined.

        Returns:
            bool: True if restricted, False otherwise
        """
        raise NotImplemented(f"Restriction {cls.__name__!r} should implement the `is_restricted` method")

    @classmethod
    def get_subclasses_by_names(cls, names: List[str]) -> List:
        if not names:
            return []
        return [subclass for subclass in cls.__subclasses__() if subclass.__name__ in names]

    @classmethod
    def get_restrictions_list(cls) -> List[str]:
        return [subclass.__name__ for subclass in cls.__subclasses__()]


class RestrictAddingWithoutDescription(Restriction):
    """Restrict adding new GraphQL types without entering
    a non-empty description."""

    @classmethod
    def is_restricted(cls, change) -> bool:
        if isinstance(change, AddedType):
            return change.type.description in (None, "")


class RestrictRemovingDescription(Restriction):
    """Restrict removing the description from an existing
    GraphQL type."""
    @classmethod
    def is_restricted(cls, change) -> bool:
        if isinstance(change, TypeDescriptionChanged):
            return change.new_desc in (None, "")
