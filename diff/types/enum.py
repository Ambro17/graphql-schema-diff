class EnumDiff:

    def __call__(self, old_enum, new_enum):
        changes = []
        old_values = set(old_enum.values)
        new_values = set(new_enum.values)

        added = new_values - old_values
        removed = old_values - new_values
        changes += added
        changes += removed

        common = old_values & new_values
        for enum in common:
            old = old_enum.values[enum]
            new = new_enum.values[enum]
            if old.description != new.description:
                changes += [(old, new)]
            if old.deprecation_reason != new.deprecation_reason:
                changes += [(old, new)]

        return changes
