from abc import abstractmethod
from enum import Enum


class Criticality(Enum):
    NonBreaking = 'NON_BREAKING'
    Dangerous = 'DANGEROUS'
    Breaking = 'BREAKING'


class Change:

    criticality = Criticality.Breaking

    @property
    def breaking(self):
        return self.criticality.value == Criticality.Breaking

    @property
    def dangerous(self):
        return self.criticality.value == Criticality.Dangerous

    @property
    def nonbreaking(self):
        return self.criticality.value == Criticality.NonBreaking

    @property
    @abstractmethod
    def message(self):
        """Formatted change message"""

    @property
    @abstractmethod
    def path(self):
        """Path to the affected schema member"""


class RemovedType(Change):
    def __init__(self, type):
        self.type = type

    def message(self):
        return f"Type '{self.type.name}' was removed"

    def path(self):
        return f'{self.type.name}'


class AddedType(Change):
    def __init__(self, added_type):
        self.type = added_type

    def message(self):
        return f"Type '{self.type.name}' was added"

    def path(self):
        return f'{self.name}'


class DescriptionChanged(Change):
    def __init__(self, new_type, name, old_field, new_field):
        self.criticality = Criticality.NonBreaking
        self.type = new_type
        self.field_name = name
        self.old_field = old_field
        self.new_field = new_field

    def message(self):
        return (
            f"Field '{self.type.name}.{self.field_name}' description changed"
            f" from '{self.old_field.description}' to '{self.new_field.description}'"
        )

    def path(self):
        return f'{self.type.name}.{self.new_field.name}'


class DeprecationReasonChanged(Change):

    def __init__(self, type, name, old_field, new_field):
        self.criticality = Criticality.NonBreaking
        self.type = type
        self.field_name = name
        self.old_field = old_field
        self.new_field = new_field

    def message(self):
        return (
            f"Deprecation reason on field '{self.type}.{self.field_name}' changed "
            f"from '{self.old_field.deprecation_reason}' to '{self.new_field.deprecation_reason}'"
        )

    def path(self):
        return f"{self.type.name}.{self.new_field.name}"


class FieldTypeChanged(Change):

    def __init__(self, type, field_name, old_field, new_field):
        self.criticality = Criticality.Breaking
        self.type = type
        self.field_name = field_name
        self.old_field = old_field
        self.new_field = new_field

    def message(self):
        return (
            f"Field '{self.type}.{self.field_name}' changed type "
            f"from '{self.old_field.type}' to '{self.new_field.type}'"
        )

    def path(self):
        return f"{self.type.name}.{self.new_field.name}"

    def safe_change(self, old_field, new_field):
        # TODO: Implement this
        return True or old_field or new_field


class SchemaQueryChange(Change):
    def __init__(self, old, new):
        self.old_keys = list(old.fields.keys())
        self.new_keys = list(new.fields.keys())

    def message(self):
        return f'Root Query changed. Old fields: {self.old_keys}. New fields: {self.new_keys}'
