from diff.types.field import Field


class ObjectType:

    def __init__(self, old, new):
        self.old = old
        self.new = new
        self.old_fields = set(old.fields)
        self.new_fields = set(new.fields)

    def diff(self):
        changes = []

        changes += self.removed_fields()
        changes += self.added_fields()

        for field in self.common_fields():
            old_field = self.old.fields[field]
            new_field = self.new.fields[field]
            changes += Field(self.new, field, old_field, new_field).diff() or []

        return changes

    def removed_fields(self):
        return self.old_fields - self.new_fields

    def added_fields(self):
        return self.new_fields - self.old_fields

    def common_fields(self):
        return self.old_fields & self.new_fields