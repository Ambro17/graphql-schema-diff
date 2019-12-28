from schemadiff.changes.argument import (
    FieldArgumentDescriptionChanged,
    FieldArgumentTypeChanged,
    FieldArgumentDefaultValueChanged,
)


class Argument:

    def __init__(self, type_, field_name, argument_name,  old_arg, new_arg):
        self.type_ = type_
        self.field_name = field_name
        self.argument_name = argument_name
        self.old_arg = old_arg
        self.new_arg = new_arg

    def diff(self):
        changes = []
        if self.old_arg.description != self.new_arg.description:
            changes.append(FieldArgumentDescriptionChanged(
                self.type_, self.field_name, self.argument_name, self.old_arg, self.new_arg
            ))
        if self.old_arg.default_value != self.new_arg.default_value:
            changes.append(FieldArgumentDefaultValueChanged(
                self.type_, self.field_name, self.argument_name, self.old_arg, self.new_arg
            ))
        if str(self.old_arg.type) != str(self.new_arg.type):
            changes.append(FieldArgumentTypeChanged(
                self.type_, self.field_name, self.argument_name, self.old_arg, self.new_arg
            ))

        return changes
