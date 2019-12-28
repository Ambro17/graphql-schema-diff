from schemadiff.changes import Change, Criticality


class InterfaceFieldAdded(Change):

    criticality = Criticality.dangerous(
        "Adding an interface to an object type may break existing clients "
        "that were not programming defensively against a new possible type."
    )

    def __init__(self, interface, field_name, field):
        self.interface = interface
        self.field_name = field_name
        self.field = field

    @property
    def message(self):
        return f"Field `{self.field_name}` of type `{self.field.type}` was added to interface `{self.interface}`"

    @property
    def path(self):
        return f"{self.interface.name}.{self.field_name}"


class InterfaceFieldRemoved(Change):

    criticality = Criticality.dangerous(
        "Removing an interface field can break existing "
        "queries that use this in a fragment spread."
    )

    def __init__(self, interface, field_name):
        self.interface = interface
        self.field_name = field_name

    @property
    def message(self):
        return f"Field `{self.field_name}` was removed from interface `{self.interface}`"

    @property
    def path(self):
        return f"{self.interface.name}.{self.field_name}"


class AbstractInterfanceChange(Change):
    def __init__(self, interface, field_name, old_field, new_field):
        self.interface = interface
        self.field_name = field_name
        self.old_field = old_field
        self.new_field = new_field

    @property
    def path(self):
        return f"{self.interface.name}.{self.field_name}"


class InterfaceFieldTypeChanged(AbstractInterfanceChange):

    @property
    def message(self):
        return (
            f"Field `{self.interface.name}.{self.field_name}` type "
            f"changed from `{self.old_field.type}` to `{self.new_field.type}`"
        )


class NewInterfaceImplemented(Change):

    criticality = Criticality.dangerous(
        "Adding an interface to an object type may break existing clients "
        "that were not programming defensively against a new possible type."
    )

    def __init__(self, interface, type_):
        self.interface = interface
        self.type_ = type_

    @property
    def message(self):
        return f"`{self.type_.name}` implements new interface `{self.interface.name}`"

    @property
    def path(self):
        return f"{self.type_}"


class DroppedInterfaceImplementation(Change):

    criticality = Criticality.breaking(
        "Removing an interface from an object type can break existing queries "
        "that use this in a fragment spread."
    )

    def __init__(self, interface, type_):
        self.interface = interface
        self.type_ = type_

    @property
    def message(self):
        return f"`{self.type_.name}` no longer implements interface `{self.interface.name}`"

    @property
    def path(self):
        return f"{self.type_}"


class InterfaceFieldDescriptionChanged(AbstractInterfanceChange):
    criticality = Criticality.safe()

    @property
    def message(self):
        return (
            f"`{self.interface.name}.{self.field_name}` description changed "
            f"from `{self.old_field.description}` to `{self.new_field.description}`"
        )


class InterfaceFieldDeprecationReasonChanged(AbstractInterfanceChange):
    criticality = Criticality.breaking('Breaking change')  # TODO: Improve this logic to check if it was deprecated before

    @property
    def message(self):
        return (
            f"`{self.interface.name}.{self.field_name}` deprecation reason changed "
            f"from `{self.old_field.deprecation_reason}` to `{self.new_field.deprecation_reason}`"
        )
