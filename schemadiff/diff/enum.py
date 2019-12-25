from schemadiff.changes.enum import (
    EnumValueAdded,
    EnumValueRemoved,
    EnumValueDescriptionChanged,
    EnumValueDeprecationReasonChanged,
)


class EnumDiff:

    def __init__(self, old_enum, new_enum):
        self.enum = new_enum
        self.old_values = old_enum.values
        self.new_values = new_enum.values

    def diff(self):
        changes = []
        old_values = set(self.old_values)
        new_values = set(self.new_values)

        added = new_values - old_values
        removed = old_values - new_values
        changes.extend(EnumValueAdded(self.enum, value) for value in added)
        changes.extend(EnumValueRemoved(self.enum, value) for value in removed)

        common = old_values & new_values
        for enum_name in common:
            old_value = self.old_values[enum_name]
            new_value = self.new_values[enum_name]
            if old_value.description != new_value.description:
                changes.append(EnumValueDescriptionChanged(self.enum, enum_name, old_value, new_value))
            if old_value.deprecation_reason != new_value.deprecation_reason:
                changes.append(EnumValueDeprecationReasonChanged(self.enum, enum_name, old_value, new_value))

        return changes
