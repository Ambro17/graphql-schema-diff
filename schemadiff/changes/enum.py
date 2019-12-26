from schemadiff.changes import Change, Criticality


class EnumValueAdded(Change):
    def __init__(self, enum, value):
        self.criticality = Criticality.dangerous(
            "Adding an enum value may break existing clients that were not "
            "programming defensively against an added case when querying an enum."
        )
        self.enum = enum
        self.value = value

    @property
    def message(self):
        return f"Enum value `{self.value}` was added to `{self.enum.name}` enum"

    @property
    def path(self):
        return f"{self.enum.name}.{self.value}"


class EnumValueRemoved(Change):
    def __init__(self, enum, value):
        self.criticality = Criticality.breaking(
            "Removing an enum value will break existing queries that use this enum value"
        )
        self.enum = enum
        self.value = value

    @property
    def message(self):
        return f"Enum value `{self.value}` was removed from `{self.enum.name}` enum"

    @property
    def path(self):
        return f"{self.enum.name}"


class EnumValueDescriptionChanged(Change):

    criticality = Criticality.safe()

    def __init__(self, enum, name, old_value, new_value):
        self.enum = enum
        self.name = name
        self.old_value = old_value
        self.new_value = new_value

    @property
    def message(self):
        if not self.old_value.description:
            msg = f"Description for enum value `{self.name}` set to `{self.new_value.description}`"
        else:
            msg = (
                f"Description for enum value `{self.name}` changed"
                f" from `{self.old_value.description}` to `{self.new_value.description}`"
            )
        return msg

    @property
    def path(self):
        return f"{self.enum.name}.{self.name}"


class EnumValueDeprecationReasonChanged(Change):

    criticality = Criticality.safe(
        "A deprecated field can still be used by clients and will give them time to adapt their queries"
    )

    def __init__(self, enum, name, old_value, new_value):
        self.enum = enum
        self.name = name
        self.old_value = old_value
        self.new_value = new_value

    @property
    def message(self):
        if not self.old_value.deprecation_reason:
            msg = (
                f"Enum value `{self.name}` was deprecated "
                f"with reason `{self.new_value.deprecation_reason}`"
            )
        else:
            msg = (
                f"Deprecation reason for enum value `{self.name}` changed "
                f"from `{self.old_value.deprecation_reason}` to `{self.new_value.deprecation_reason}`"
            )
        return msg

    @property
    def path(self):
        return f"{self.enum.name}.{self.name}"