from graphql import is_non_null_type

from schemadiff.changes import Change, Criticality, is_safe_change_for_input_value


class DirectiveChange(Change):

    @property
    def path(self):
        return f"{self.directive}"


class AddedDirective(DirectiveChange):

    criticality = Criticality.safe()

    def __init__(self, directive, directive_locations):
        self.directive = directive
        self.directive_locations = directive_locations

    @property
    def message(self):
        locations = ' | '.join(loc.name for loc in self.directive_locations)
        return f"Directive `{self.directive}` was added to use on `{locations}`"


class RemovedDirective(DirectiveChange):

    criticality = Criticality.breaking("Removing a directive may break clients that depend on them.")

    def __init__(self, directive):
        self.directive = directive

    @property
    def message(self):
        return f"Directive `{self.directive}` was removed"


class DirectiveDescriptionChanged(DirectiveChange):
    criticality = Criticality.safe()

    def __init__(self, old, new):
        self.old = old
        self.new = new

    @property
    def message(self):
        return (
            f"Description for directive `{self.new!s}` "
            f"changed from `{self.old.description}` to `{self.new.description}`"
        )

    @property
    def path(self):
        return f"{self.new}"


class DirectiveLocationsChanged(DirectiveChange):
    def __init__(self, directive, old_locations, new_locations):
        self.directive = directive
        self.old_locations = old_locations
        self.new_locations = new_locations
        self.criticality = (
            Criticality.safe() if self._only_additions() else Criticality.breaking(
                "Removing a directive location will break any instance of its usage. "
                "Be sure no one uses it before removing it"
            )
        )

    def _only_additions(self):
        new_location_names = {l.name for l in self.new_locations}
        return all(l.name in new_location_names for l in self.old_locations)

    @property
    def message(self):
        return (
            f"Directive locations of `{self.directive!s}` changed "
            f"from `{' | '.join(l.name for l in self.old_locations)}` "
            f"to `{' | '.join(l.name for l in self.new_locations)}`"
        )


class DirectiveArgumentAdded(DirectiveChange):
    def __init__(self, directive, arg_name, arg_type):
        self.criticality = Criticality.safe() if not is_non_null_type(arg_type.type) else Criticality.breaking(
            "Adding a non nullable directive argument will break existing usages of the directive"
        )
        self.directive = directive
        self.arg_name = arg_name
        self.arg_type = arg_type

    @property
    def message(self):
        return f"Added argument `{self.arg_name}: {self.arg_type.type}` to `{self.directive!s}` directive"


class DirectiveArgumentRemoved(DirectiveChange):

    criticality = Criticality.breaking("Removing a directive argument will break existing usages of the argument")

    def __init__(self, directive, arg_name, arg_type):
        self.directive = directive
        self.arg_name = arg_name
        self.arg_type = arg_type

    @property
    def message(self):
        return f"Removed argument `{self.arg_name}: {self.arg_type.type}` from `{self.directive!s}` directive"


class DirectiveArgumentTypeChanged(DirectiveChange):
    def __init__(self, directive, arg_name, old_type, new_type):
        self.criticality = (
            Criticality.breaking("Changing the argument type is a breaking change")
            if not is_safe_change_for_input_value(old_type, new_type)
            else Criticality.safe("Changing an input field from non-null to null is considered non-breaking")
        )
        self.directive = directive
        self.arg_name = arg_name
        self.old_type = old_type
        self.new_type = new_type

    @property
    def message(self):
        return (
            f"Type for argument `{self.arg_name}` on `{self.directive!s}` directive changed "
            f"from `{self.old_type}` to `{self.new_type}`"
        )


class DirectiveArgumentDefaultChanged(DirectiveChange):
    def __init__(self, directive, arg_name, old_default, new_default):
        self.criticality = Criticality.dangerous(
            "Changing the default value for an argument may change the runtime "
            "behaviour of a field if it was never provided."
          )
        self.directive = directive
        self.arg_name = arg_name
        self.old_default = old_default
        self.new_default = new_default

    @property
    def message(self):
        return (
            f"Default value for argument `{self.arg_name}` on `{self.directive!s}` directive changed "
            f"from `{self.old_default!r}` to `{self.new_default!r}`"
        )


class DirectiveArgumentDescriptionChanged(DirectiveChange):
    criticality = Criticality.safe()

    def __init__(self, directive, arg_name, old_desc, new_desc):
        self.directive = directive
        self.arg_name = arg_name
        self.old_desc = old_desc
        self.new_desc = new_desc

    @property
    def message(self):
        return (
            f"Description for argument `{self.arg_name}` on `{self.directive!s}` directive changed "
            f"from `{self.old_desc}` to `{self.new_desc}`"
        )
