from schemadiff.changes.type import TypeDescriptionChanged, AddedType
from typing import List
from abc import ABC


RESTRICT_ADDING_WITHOUT_DESC = 'RESTRICT_ADDING_WITHOUT_DESC'
RESTRICTIONS = [RESTRICT_ADDING_WITHOUT_DESC]


class Restriction(ABC):
    @classmethod
    def evaluate(cls, change):
        pass


class RestrictAddingWithoutDescription(Restriction):
    @classmethod
    def evaluate(cls, change):
        if isinstance(change, AddedType):
            return not change.type.description


class RestrictRemovingDescription(Restriction):
    @classmethod
    def evaluate(cls, change):
        if isinstance(change, TypeDescriptionChanged):
            return not change


def is_restricted(change, restrictions: List[str]):
    """True if the change is restricted, False otherwise"""
    restrictions_cls = [r for r in Restriction.__subclasses__() if r.__name__ in restrictions]
    return any(restriction.evaluate(change) for restriction in restrictions_cls)


def load_restrictions():
    return [cls.__name__ for cls in Restriction.__subclasses__()]
