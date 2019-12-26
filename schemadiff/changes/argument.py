from schemadiff.changes import Change, Criticality, is_safe_change_for_input_value


class FieldAbstractArgumentChange(Change):
    def __init__(self, parent_type, field, arg_name, old_arg, new_arg):
        self.parent = parent_type
        self.field_name = field
        self.arg_name = arg_name
        self.old_arg = old_arg
        self.new_arg = new_arg

    @property
    def path(self):
        return f"{self.parent.name}.{self.field_name}"


class FieldArgumentDescriptionChanged(FieldAbstractArgumentChange):

    criticality = Criticality.safe()

    @property
    def message(self):
        return (
            f"Description for argument `{self.arg_name}` on field `{self.parent}.{self.field_name}` "
            f"changed from `{self.old_arg.description}` to `{self.new_arg.description}`"
        )


class FieldArgumentDefaultValueChanged(FieldAbstractArgumentChange):
    criticality = Criticality.dangerous(
        "Changing the default value for an argument may change the runtime "
        "behaviour of a field if it was never provided."
    )

    @property
    def message(self):
        return (
            f"Default value for argument `{self.arg_name}` on field `{self.parent}.{self.field_name}` "
            f"changed from `{self.old_arg.default_value!r}` to `{self.new_arg.default_value!r}`"
        )


class FieldArgumentTypeChanged(FieldAbstractArgumentChange):

    def __init__(self, parent_type, field, arg_name, old_arg, new_arg):
        super().__init__(parent_type, field, arg_name, old_arg, new_arg)
        self.criticality = (
                Criticality.safe()
                if is_safe_change_for_input_value(old_arg.type, new_arg.type)
                else Criticality.breaking(
                    "Changing the type of a field's argument can break existing queries that use this argument."
                )
        )

    @property
    def message(self):
        return (
            f"Type for argument `{self.arg_name}` on field `{self.parent}.{self.field_name}` "
            f"changed from `{self.old_arg.type}` to `{self.new_arg.type}`"
        )
