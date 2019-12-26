from graphql import is_non_null_type

from schemadiff.changes import Change, Criticality, is_safe_type_change


class FieldDescriptionChanged(Change):

    criticality = Criticality.safe()

    def __init__(self, new_type, name, old_field, new_field):
        self.type = new_type
        self.field_name = name
        self.old_field = old_field
        self.new_field = new_field

    @property
    def message(self):
        return (
            f"`{self.type.name}.{self.field_name}` description changed"
            f" from `{self.old_field.description}` to `{self.new_field.description}`"
        )

    @property
    def path(self):
        return f'{self.type}.{self.field_name}'


class FieldDeprecationReasonChanged(Change):

    criticality = Criticality.safe()

    def __init__(self, type, name, old_field, new_field):
        self.type = type
        self.field_name = name
        self.old_field = old_field
        self.new_field = new_field

    @property
    def message(self):
        return (
            f"Deprecation reason on field `{self.type}.{self.field_name}` changed "
            f"from `{self.old_field.deprecation_reason}` to `{self.new_field.deprecation_reason}`"
        )

    @property
    def path(self):
        return f"{self.type}.{self.field_name}"


class FieldTypeChanged(Change):

    def __init__(self, type, field_name, old_field, new_field):
        self.criticality = Criticality.safe()\
                           if is_safe_type_change(old_field.type, new_field.type)\
                           else Criticality.breaking('Changing a field type will break queries that assume its type')
        self.type = type
        self.field_name = field_name
        self.old_field = old_field
        self.new_field = new_field

    @property
    def message(self):
        return (
            f"`{self.type}.{self.field_name}` type changed "
            f"from `{self.old_field.type}` to `{self.new_field.type}`"
        )

    @property
    def path(self):
        return f"{self.type}.{self.field_name}"


class FieldArgumentAdded(Change):
    def __init__(self, parent, field_name, argument_name, arg_type):
        self.criticality = Criticality.safe('Adding an optional argument is a safe change')\
                           if not is_non_null_type(arg_type.type)\
                           else Criticality.breaking("Adding a required argument to an existing field is a breaking "
                                                   "change because it will break existing uses of this field")
        self.parent = parent
        self.field_name = field_name
        self.argument_name = argument_name
        self.arg_type = arg_type

    @property
    def message(self):
        return (
            f"Argument `{self.argument_name}: {self.arg_type.type}` "
            f"added to `{self.parent.name}.{self.field_name}`"
        )

    @property
    def path(self):
        return f"{self.parent}.{self.field_name}"


class FieldArgumentRemoved(Change):

    criticality = Criticality.breaking(
        "Removing a field argument will break queries that use this argument"
    )

    def __init__(self, parent, field_name, argument_name):
        self.parent = parent
        self.field_name = field_name
        self.argument_name = argument_name

    @property
    def message(self):
        return (
            f"Removed argument `{self.argument_name}` from `{self.parent.name}.{self.field_name}`"
        )

    @property
    def path(self):
        return f"{self.parent}.{self.field_name}"
