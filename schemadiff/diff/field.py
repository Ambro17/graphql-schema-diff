from schemadiff.changes.field import (
    FieldDescriptionChanged,
    FieldDeprecationReasonChanged,
    FieldTypeChanged,
    FieldArgumentAdded,
    FieldArgumentRemoved
)
from schemadiff.diff.argument import Argument


class Field:

    def __init__(self, type, name, old_field, new_field):
        self.type = type
        self.field_name = name
        self.old_field = old_field
        self.new_field = new_field
        self.old_args = set(old_field.args)
        self.new_args = set(new_field.args)

    def diff(self):
        changes = []

        if self.old_field.description != self.new_field.description:
            changes.append(FieldDescriptionChanged(self.type, self.field_name, self.old_field, self.new_field))

        if self.old_field.deprecation_reason != self.new_field.deprecation_reason:
            changes.append(FieldDeprecationReasonChanged(self.type, self.field_name, self.old_field, self.new_field))

        if str(self.old_field.type) != str(self.new_field.type):
            changes.append(FieldTypeChanged(self.type, self.field_name, self.old_field, self.new_field))

        added = self.new_args - self.old_args
        removed = self.old_args - self.new_args

        changes.extend(
            FieldArgumentAdded(self.type, self.field_name, arg_name, self.new_field.args[arg_name])
            for arg_name in added
        )
        changes.extend(
            FieldArgumentRemoved(self.type, self.field_name, arg_name)
            for arg_name in removed
        )

        common_arguments = self.common_arguments()
        for arg_name in common_arguments:
            old_arg = self.old_field.args[arg_name]
            new_arg = self.new_field.args[arg_name]
            changes += Argument(self.type, self.field_name, arg_name, old_arg, new_arg).diff() or []

        return changes

    def common_arguments(self):
        return self.old_args & self.new_args
