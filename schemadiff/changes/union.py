from schemadiff.changes import Change, Criticality


class UnionMemberAdded(Change):

    criticality = Criticality.dangerous(
        "Adding a possible type to Unions may break existing clients "
        "that were not programming defensively against a new possible type."
    )

    def __init__(self, union, value):
        self.union = union
        self.value = value

    @property
    def message(self):
        return f"Union member `{self.value}` was added to `{self.union.name}` Union type"

    @property
    def path(self):
        return f"{self.union.name}"


class UnionMemberRemoved(Change):

    criticality = Criticality.breaking(
        'Removing a union member from a union can break '
        'queries that use this union member in a fragment spread'
    )

    def __init__(self, union, value):
        self.union = union
        self.value = value

    @property
    def message(self):
        return f"Union member `{self.value}` was removed from `{self.union.name}` Union type"

    @property
    def path(self):
        return f"{self.union.name}"
