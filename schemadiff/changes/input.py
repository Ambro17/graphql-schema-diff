from graphql import is_non_null_type

from schemadiff.changes import Change, Criticality, is_safe_change_for_input_value


class InputFieldAdded(Change):

    BREAKING_MSG = (
        "Adding a non-null field to an existing input type will cause existing "
        "queries that use this input type to break because they will "
        "not provide a value for this new field."
    )

    def __init__(self, input_object, field_name, field):
        self.criticality = (
            Criticality.safe()
            if is_non_null_type(field.type) is False
            else Criticality.breaking(self.BREAKING_MSG)
        )

        self.input_object = input_object
        self.field_name = field_name
        self.field = field

    @property
    def message(self):
        return f"Input Field `{self.field_name}: {self.field.type}` was added to input type `{self.input_object}`"

    @property
    def path(self):
        return f"{self.input_object}.{self.field_name}"


class InputFieldRemoved(Change):

    criticality = Criticality.breaking(
        'Removing an input field will break queries that use this input field.'
    )

    def __init__(self, input_object, value):
        self.input_object = input_object
        self.value = value

    @property
    def message(self):
        return f"Input Field `{self.value}` removed from input type `{self.input_object}`"

    @property
    def path(self):
        return f"{self.input_object}.{self.value}"


class InputFieldDescriptionChanged(Change):

    criticality = Criticality.safe()

    def __init__(self, input, name, new_field, old_field):
        self.input = input
        self.name = name
        self.new_field = new_field
        self.old_field = old_field

    @property
    def message(self):
        return (
            f"Description for Input field `{self.input.name}.{self.name}` "
            f"changed from `{self.old_field.description}` to `{self.new_field.description}`"
        )

    @property
    def path(self):
        return f"{self.input.name}.{self.name}"


class InputFieldDefaultChanged(Change):

    criticality = Criticality.dangerous(
        "Changing the default value for an argument may change the runtime "
        "behaviour of a field if it was never provided."
    )

    def __init__(self, input, name, new_field, old_field):
        self.input = input
        self.name = name
        self.new_field = new_field
        self.old_field = old_field

    @property
    def message(self):
        return (
            f"Default value for input field `{self.input.name}.{self.name}` "
            f"changed from `{self.old_field.default_value!r}` to `{self.new_field.default_value!r}`"
        )

    @property
    def path(self):
        return f"{self.input.name}.{self.name}"


class InputFieldTypeChanged(Change):
    def __init__(self, input, name, new_field, old_field):
        self.criticality = (
            Criticality.safe()
            if is_safe_change_for_input_value(old_field.type, new_field.type)
            else Criticality.breaking(
                "Changing the type of an input field can break existing queries that use this field"
            )
        )
        self.input = input
        self.name = name
        self.new_field = new_field
        self.old_field = old_field

    @property
    def message(self):
        return (
            f"`{self.input.name}.{self.name}` type changed from "
            f"`{self.old_field.type}` to `{self.new_field.type}`"
        )

    @property
    def path(self):
        return f"{self.input.name}.{self.name}"