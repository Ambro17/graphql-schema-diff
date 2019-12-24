from schemadiff.changes.directive import (
    DirectiveDescriptionChanged,
    DirectiveLocationsChanged,
    DirectiveArgumentAdded,
    DirectiveArgumentRemoved,
    DirectiveArgumentTypeChanged,
    DirectiveArgumentDefaultChanged,
    DirectiveArgumentDescriptionChanged,
)


class Directive:
    def __init__(self, old_directive, new_directive):
        self.old_directive = old_directive
        self.new_directive = new_directive
        self.old_arguments = set(old_directive.args)
        self.new_arguments = set(new_directive.args)

    def diff(self):
        changes = []
        if self.old_directive.description != self.new_directive.description:
            changes.append(DirectiveDescriptionChanged(self.old_directive, self.new_directive))
        if self.old_directive.locations != self.new_directive.locations:
            changes.append(DirectiveLocationsChanged(
                self.new_directive, self.old_directive.locations, self.new_directive.locations
            ))

        removed = self.old_arguments - self.new_arguments
        added = self.new_arguments - self.old_arguments
        changes.extend(DirectiveArgumentAdded(self.new_directive, argument_name, self.new_directive.args[argument_name])
                       for argument_name in added)
        changes.extend(DirectiveArgumentRemoved(self.new_directive, argument_name, self.old_directive.args[argument_name])
                       for argument_name in removed)

        for arg_name in self.old_arguments & self.new_arguments:
            old_arg = self.old_directive.args[arg_name]
            new_arg = self.new_directive.args[arg_name]
            changes += DirectiveArgument(self.new_directive, arg_name, old_arg, new_arg).diff()

        return changes


class DirectiveArgument:
    def __init__(self, directive, arg_name, old_arg, new_arg):
        self.directive = directive
        self.arg_name = arg_name
        self.old_arg = old_arg
        self.new_arg = new_arg

    def diff(self):
        changes = []
        if str(self.old_arg.type) != str(self.new_arg.type):
            changes.append(DirectiveArgumentTypeChanged(
                self.directive, self.arg_name, self.old_arg.type, self.new_arg.type
            ))
        if self.old_arg.default_value != self.new_arg.default_value:
            changes.append(DirectiveArgumentDefaultChanged(
                self.directive, self.arg_name, self.old_arg.default_value, self.new_arg.default_value
            ))
        if self.old_arg.description != self.new_arg.description:
            changes.append(DirectiveArgumentDescriptionChanged(
                self.directive, self.arg_name, self.old_arg.description, self.new_arg.description
            ))

        return changes
