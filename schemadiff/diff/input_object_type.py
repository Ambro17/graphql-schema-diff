from schemadiff.changes.input import (
    InputFieldAdded,
    InputFieldRemoved,
    InputFieldDescriptionChanged,
    InputFieldDefaultChanged,
    InputFieldTypeChanged,
)


class InputObjectType:
    def __init__(self, old_type, new_type):
        self.type = new_type
        self.old_fields = old_type.fields
        self.new_fields = new_type.fields

    def diff(self):
        changes = []

        old_field_names = set(self.old_fields)
        new_field_names = set(self.new_fields)

        added = new_field_names - old_field_names
        removed = old_field_names - new_field_names

        changes.extend(InputFieldAdded(self.type, field_name, self.new_fields[field_name]) for field_name in added)
        changes.extend(InputFieldRemoved(self.type, field_name) for field_name in removed)

        common_types = old_field_names & new_field_names
        for type_name in common_types:
            old = self.old_fields[type_name]
            new = self.new_fields[type_name]
            if str(old.type) != str(new.type):
                changes.append(InputFieldTypeChanged(self.type, type_name, new, old))
            if old.description != new.description:
                changes.append(InputFieldDescriptionChanged(self.type, type_name, new, old))
            if old.default_value != new.default_value:
                changes.append(InputFieldDefaultChanged(self.type, type_name, new, old))

        return changes
