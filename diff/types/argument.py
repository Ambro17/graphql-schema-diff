from diff.changes import ArgumentDescriptionChanged, ArgumentTypeChanged, ArgumentDefaultValueChanged


class Argument:

    def __init__(self, type, field_name, argument_name,  old_arg, new_arg):
        self.type = type
        self.field_name = field_name
        self.argument_name = argument_name
        self.old_arg = old_arg
        self.new_arg = new_arg

    def diff(self):
        changes = []
        if self.old_arg.description != self.new_arg.description:
            changes.append(ArgumentDescriptionChanged())
        if self.old_arg.default_value != self.new_arg.default_value:
            changes.append(ArgumentDefaultValueChanged())
        if str(self.old_arg.type) != str(self.new_arg.type):
            changes.append(ArgumentTypeChanged(self.type, self.field_name, self.argument_name,
                                               self.old_arg, self.new_arg))

        return changes
