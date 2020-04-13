from schemadiff.changes import Change, Criticality


class SchemaChange(Change):
    criticality = Criticality.breaking('Changing a root type is a breaking change')

    def __init__(self, old_type, new_type):
        self.old_type = old_type
        self.new_type = new_type

    @property
    def path(self):
        return self.new_type


class SchemaQueryTypeChanged(SchemaChange):

    @property
    def message(self):
        return f"Schema query root has changed from `{self.old_type}` to `{self.new_type}`"


class SchemaMutationTypeChanged(SchemaChange):

    @property
    def message(self):
        return f"Schema mutation root has changed from `{self.old_type}` to `{self.new_type}`"


class SchemaSubscriptionTypeChanged(SchemaChange):

    @property
    def message(self):
        return f"Schema subscription root has changed from `{self.old_type}` to `{self.new_type}`"
