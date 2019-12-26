from abc import abstractmethod, ABC
from enum import Enum

from attr import dataclass
from graphql import is_wrapping_type, is_non_null_type, is_list_type


class Criticality(Enum):
    NonBreaking = 'NON_BREAKING'
    Dangerous = 'DANGEROUS'
    Breaking = 'BREAKING'


@dataclass
class ApiChange:
    level: Criticality
    reason: str

    SAFE_CHANGE = "This change won't break any preexisting query"

    @classmethod
    def breaking(cls, reason):
        return cls(level=Criticality.Breaking, reason=reason)

    @classmethod
    def dangerous(cls, reason):
        return cls(level=Criticality.Dangerous, reason=reason)

    @classmethod
    def safe(cls, reason=SAFE_CHANGE):
        return cls(level=Criticality.NonBreaking, reason=reason)


def is_safe_type_change(old_type, new_type) -> bool:
    """Depending on the old an new type, a field type change may be breaking, dangerous or safe

    * If both fields are 'leafs' in the sense they don't wrap an inner type, just compare their type.
    * If the new type has a non-null constraint, check that it was already non-null and compare against the contained
      type. If the contraint is new, just compare with old_type
    * If the old type is a list and the new one too, compare their inner type
      If the new type has a non-null constraint, compare against the wrapped type
    """
    if not is_wrapping_type(old_type) and not is_wrapping_type(new_type):
        return str(old_type) == str(new_type)
    if is_non_null_type(new_type):
        # Grab the inner type it it also was non null.
        of_type = old_type.of_type if is_non_null_type(old_type) else old_type
        return is_safe_type_change(of_type, new_type.of_type)

    if is_list_type(old_type):
        # If both types are lists, compare their inner type.
        # If the new type has a non-null constraint, compare with its inner type (may be a list or not)
        return (
            (
                    is_list_type(new_type) and is_safe_type_change(old_type.of_type, new_type.of_type)
            )
            or
            (
                    is_non_null_type(new_type) and is_safe_type_change(old_type, new_type.of_type)
            )
        )

    return False


def is_safe_change_for_input_value(old_type, new_type):
    if not is_wrapping_type(old_type) and not is_wrapping_type(new_type):
        return str(old_type) == str(new_type)
    if is_list_type(old_type) and is_list_type(new_type):
        return is_safe_change_for_input_value(old_type.of_type, new_type.of_type)

    if is_non_null_type(old_type):
        # Grab the inner type it it also was non null.
        of_type = new_type.of_type if is_non_null_type(new_type) else new_type
        return is_safe_type_change(old_type.of_type, of_type)

    return False


class Change(ABC):

    criticality: ApiChange

    @property
    def breaking(self):
        return self.criticality.level == Criticality.Breaking

    @property
    def dangerous(self):
        return self.criticality.level == Criticality.Dangerous

    @property
    def safe(self):
        return self.criticality.level == Criticality.NonBreaking

    @property
    @abstractmethod
    def message(self):
        """Formatted change message"""

    @property
    @abstractmethod
    def path(self):
        """Path to the affected schema member"""
