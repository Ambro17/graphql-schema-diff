from schemadiff.changes.object import ObjectTypeFieldAdded, ObjectTypeFieldRemoved
from schemadiff.changes.interface import NewInterfaceImplemented, DroppedInterfaceImplementation
from schemadiff.diff.field import Field


class ObjectType:

    def __init__(self, old, new):
        self.old = old
        self.new = new

        self.old_field_names = set(old.fields)
        self.new_field_names = set(new.fields)

        self.old_interfaces = set(old.interfaces)
        self.new_interfaces = set(new.interfaces)

    def diff(self):
        changes = []

        # Added and removed fields
        added = self.new_field_names - self.old_field_names
        removed = self.old_field_names - self.new_field_names
        changes.extend(ObjectTypeFieldAdded(self.new, field_name, self.new.fields[field_name]) for field_name in added)
        changes.extend(ObjectTypeFieldRemoved(self.new, field_name, self.old.fields[field_name])
                       for field_name in removed)

        # Added and removed interfaces
        added = self.added_interfaces()
        removed = self.removed_interfaces()
        changes.extend(NewInterfaceImplemented(interface, self.new) for interface in added)
        changes.extend(DroppedInterfaceImplementation(interface, self.new) for interface in removed)

        for field_name in self.common_fields():
            old_field = self.old.fields[field_name]
            new_field = self.new.fields[field_name]
            changes += Field(self.new, field_name, old_field, new_field).diff() or []

        return changes

    def common_fields(self):
        return self.old_field_names & self.new_field_names

    def added_interfaces(self):
        """Compare interfaces equality by name. Internal diffs are solved later"""
        old_interface_names = {str(x) for x in self.old_interfaces}
        return [interface for interface in self.new_interfaces
                if str(interface) not in old_interface_names]

    def removed_interfaces(self):
        """Compare interfaces equality by name. Internal diffs are solved later"""
        new_interface_names = {str(x) for x in self.new_interfaces}
        return [interface for interface in self.old_interfaces
                if str(interface) not in new_interface_names]