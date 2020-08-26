from schemadiff.changes.type import TypeDescriptionChanged, AddedType
from typing import List

RESTRICT_ADDING_WITHOUT_DESC = 'RESTRICT_ADDING_WITHOUT_DESC'
RESTRICTIONS = [RESTRICT_ADDING_WITHOUT_DESC]


def is_restricted(change, restrictions: List[str]):
    """True if the change is restricted, False otherwise"""
    if RESTRICT_ADDING_WITHOUT_DESC in restrictions:
        """Restrict the addition or changing of any field
        without entering a valid description."""
        if isinstance(change, AddedType):
            return not change.type.description

        if isinstance(change, TypeDescriptionChanged):
            return not change

    return True