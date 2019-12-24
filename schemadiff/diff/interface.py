from schemadiff.changes.interface import InterfaceFieldAdded, InterfaceFieldRemoved
from schemadiff.diff.field import Field


class InterfaceType:

    def __init__(self, old_interface, new_interface):
        self.old_face = old_interface
        self.new_face = new_interface

        self.old_fields = set(old_interface.fields)
        self.new_fields = set(new_interface.fields)

    def diff(self):
        changes = []

        added = self.new_fields - self.old_fields
        removed = self.old_fields - self.new_fields
        changes.extend(InterfaceFieldAdded(self.new_face, name, self.new_face.fields[name]) for name in added)
        changes.extend(InterfaceFieldRemoved(self.new_face, field_name) for field_name in removed)

        common = self.old_fields & self.new_fields
        for field_name in common:
            old_field = self.old_face.fields[field_name]
            new_field = self.new_face.fields[field_name]

            changes += Field(self.new_face, field_name, old_field, new_field).diff() or []

        return changes
