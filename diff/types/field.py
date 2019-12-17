from diff.change_types import DescriptionChanged, DeprecationReasonChanged, FieldTypeChanged


class Field:

    def __init__(self, type, name, old_field, new_field):
        self.type = type
        self.field_name = name
        self.old_field = old_field
        self.new_field = new_field

    def diff(self):
        changes = []

        if self.old_field.description != self.new_field.description:
            changes.append(DescriptionChanged(self.type, self.field_name, self.old_field, self.new_field))

        if self.old_field.deprecation_reason != self.new_field.deprecation_reason:
            changes.append(DeprecationReasonChanged(self.type, self.field_name, self.old_field, self.new_field))

        if str(self.old_field.type) != str(self.new_field.type):
            changes.append(FieldTypeChanged(self.type, self.field_name, self.old_field, self.new_field))

        return changes
