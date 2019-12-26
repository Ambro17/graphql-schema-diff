from schemadiff.changes import Change, Criticality


class ObjectTypeFieldAdded(Change):

    criticality = Criticality.safe()

    def __init__(self, parent, field_name):
        self.parent = parent
        self.field_name = field_name

    @property
    def message(self):
        return f"Field `{self.field_name}` was added to object type `{self.parent.name}`"

    @property
    def path(self):
        return f"{self.parent.name}.{self.field_name}"


class ObjectTypeFieldRemoved(Change):

    def __init__(self, parent, field_name, field):
        self.parent = parent
        self.field_name = field_name
        self.field = field
        self.criticality = (
            Criticality.dangerous(
                "Removing deprecated fields without sufficient time for clients "
                "to update their queries may break their code"
            ) if field.deprecation_reason else Criticality.breaking(
                "Removing a field is a breaking change. It is preferred to deprecate the field before removing it."
            )
        )

    @property
    def message(self):
        return f"Field `{self.field_name}` was removed from object type `{self.parent.name}`"

    @property
    def path(self):
        return f"{self.parent.name}.{self.field_name}"
