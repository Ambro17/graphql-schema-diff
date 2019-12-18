from diff.changes import (
    InputObjectTypeAdded,
    InputObjectTypeRemoved,
    InputObjectTypeDescriptionChanged,
    InputTypeDefaultChanged,
    InputObjectTypeTypeChanged,
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

        changes.extend(InputObjectTypeAdded(self.type, value) for value in added)
        changes.extend(InputObjectTypeRemoved(self.type, value) for value in removed)

        common_types = old_field_names & new_field_names
        for type_name in common_types:
            old = self.old_fields[type_name]
            new = self.new_fields[type_name]
            if str(old.type) != str(new.type):
                changes.append(InputObjectTypeTypeChanged(self.type, type_name, new, old))
            if old.description != new.description:
                changes.append(InputObjectTypeDescriptionChanged(self.type, type_name, new, old))
            if old.default_value != new.default_value:
                changes.append(InputTypeDefaultChanged(self.type, type_name, new, old))

        return changes
