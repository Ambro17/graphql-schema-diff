from schemadiff.changes import Change, Criticality


class RemovedType(Change):

    criticality = Criticality.breaking(
        "Removing a type is a breaking change. "
        "It is preferred to deprecate and remove all references to this type first."
    )

    def __init__(self, type):
        self.type = type

    @property
    def message(self):
        return f"Type `{self.type.name}` was removed"

    @property
    def path(self):
        return f'{self.type.name}'


class AddedType(Change):

    criticality = Criticality.safe()

    def __init__(self, added_type):
        self.type = added_type

    @property
    def message(self):
        return f"Type `{self.type.name}` was added"

    @property
    def path(self):
        return f'{self.type.name}'


class TypeDescriptionChanged(Change):

    criticality = Criticality.safe()

    def __init__(self, type_name, old_desc, new_desc):
        self.type = type_name
        self.old_desc = old_desc
        self.new_desc = new_desc

    @property
    def message(self):
        return (
            f"Description for type `{self.type}` changed from "
            f"`{self.old_desc}` to `{self.new_desc}`"
        )

    @property
    def path(self):
        return self.type


class TypeKindChanged(Change):
    criticality = Criticality.breaking(
        "Changing the kind of a type is a breaking change because "
        "it can cause existing queries to error. "
        "For example, turning an object type to a scalar type "
        "would break queries that define a selection set for this type."
    )

    def __init__(self, type, old_kind, new_kind):
        self.type = type
        self.old_kind = old_kind
        self.new_kind = new_kind

    @property
    def message(self):
        return f"`{self.type}` kind changed from `{self.old_kind.value.upper()}` to `{self.new_kind.value.upper()}`"

    @property
    def path(self):
        return f"{self.type}"