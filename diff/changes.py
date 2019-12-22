from abc import abstractmethod
from enum import Enum


class Criticality(Enum):
    NonBreaking = 'NON_BREAKING'
    Dangerous = 'DANGEROUS'
    Breaking = 'BREAKING'


class Change:

    criticality = Criticality.Breaking

    @property
    def breaking(self):
        return self.criticality.value == Criticality.Breaking

    @property
    def dangerous(self):
        return self.criticality.value == Criticality.Dangerous

    @property
    def nonbreaking(self):
        return self.criticality.value == Criticality.NonBreaking

    @property
    @abstractmethod
    def message(self):
        """Formatted change message"""

    @property
    @abstractmethod
    def path(self):
        """Path to the affected schema member"""


class RemovedType(Change):
    def __init__(self, type):
        self.type = type

    def message(self):
        return f"Type `{self.type.name}` was removed"

    def path(self):
        return f'{self.type.name}'


class AddedType(Change):
    def __init__(self, added_type):
        self.type = added_type

    def message(self):
        return f"Type `{self.type.name}` was added"

    def path(self):
        return f'{self.type.type}'


class DescriptionChanged(Change):
    def __init__(self, new_type, name, old_field, new_field):
        self.criticality = Criticality.NonBreaking
        self.type = new_type
        self.field_name = name
        self.old_field = old_field
        self.new_field = new_field

    def message(self):
        return (
            f"Field `{self.type.name}.{self.field_name}` description changed"
            f" from `{self.old_field.description}` to `{self.new_field.description}`"
        )

    def path(self):
        return f'{self.type.name}.{self.new_field.name}'


class DeprecationReasonChanged(Change):

    def __init__(self, type, name, old_field, new_field):
        self.criticality = Criticality.NonBreaking
        self.type = type
        self.field_name = name
        self.old_field = old_field
        self.new_field = new_field

    def message(self):
        return (
            f"Deprecation reason on field `{self.type}.{self.field_name}` changed "
            f"from `{self.old_field.deprecation_reason}` to `{self.new_field.deprecation_reason}`"
        )

    def path(self):
        return f"{self.type.name}.{self.new_field.name}"


class FieldTypeChanged(Change):

    def __init__(self, type, field_name, old_field, new_field):
        self.criticality = Criticality.Breaking
        self.type = type
        self.field_name = field_name
        self.old_field = old_field
        self.new_field = new_field

    def message(self):
        return (
            f"Field `{self.type}.{self.field_name}` changed type "
            f"from `{self.old_field.type}` to `{self.new_field.type}`"
        )

    def path(self):
        return f"{self.type.name}.{self.new_field.name}"

    def safe_change(self, old_field, new_field):
        # TODO: Implement this
        return True or old_field or new_field


#  ============== ENUMS ==============


class EnumValueAdded(Change):
    def __init__(self, enum, value):
        self.criticality = Criticality.Breaking
        self.enum = enum
        self.value = value

    def message(self):
        return f"Enum value `{self.value}` was added to `{self.enum.name}` enum"

    def path(self):
        return f"{self.enum.name}.{self.value.name}"


class EnumValueRemoved(Change):
    def __init__(self, enum, value):
        self.criticality = Criticality.Breaking
        self.enum = enum
        self.value = value

    def message(self):
        return f"Enum value `{self.value}` was removed from `{self.enum.name}` enum"

    def path(self):
        return f"{self.enum.name}.{self.value.name}"


class EnumValueDescriptionChanged(Change):
    def __init__(self, enum, name, old_value, new_value):
        self.criticality = Criticality.NonBreaking
        self.enum = enum
        self.name = name
        self.old_value = old_value
        self.new_value = new_value

    def message(self):
        if not self.old_value.description:
            msg = f"Description for enum value `{self.name}` set to `{self.new_value.description}`"
        else:
            msg = (
                f"Description for enum value `{self.name}` changed"
                f" from `{self.old_value.description}` to `{self.new_value.description}`"
            )
        return msg

    def path(self):
        return f"{self.enum.name}.{self.name}"


class EnumValueDeprecationReasonChanged(Change):
    def __init__(self, enum, name, old_value, new_value):
        self.criticality = Criticality.NonBreaking
        self.enum = enum
        self.name = name
        self.old_value = old_value
        self.new_value = new_value

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

    def path(self):
        return f"{self.enum.name}.{self.name}"


#  ============== Union ==============

class UnionMemberAdded(Change):
    def __init__(self, union, value):
        self.criticality = Criticality.Breaking
        self.union = union
        self.value = value

    def message(self):
        return f"Union member `{self.value}` was added to `{self.union.name}` Union type"

    def path(self):
        return f"{self.union.name}.{self.value.name}"


class UnionMemberRemoved(Change):
    def __init__(self, union, value):
        self.criticality = Criticality.Breaking
        self.union = union
        self.value = value

    def message(self):
        return f"Union member `{self.value}` was removed from `{self.union.name}` Union type"

    def path(self):
        return f"{self.union.name}.{self.value.name}"


#  ============== Input Objects ==============


class InputObjectTypeAdded(Change):
    def __init__(self, input_object, field_name, field):
        self.criticality = Criticality.Breaking
        self.input_object = input_object
        self.field_name = field_name
        self.field = field

    def message(self):
        return f"Input Field `{self.field_name}: {self.field.type}` was added to input type `{self.input_object}`"

    def path(self):
        return f"{self.input_object.name}.{self.field_name}"


class InputObjectTypeRemoved(Change):
    def __init__(self, input_object, value):
        self.criticality = Criticality.Breaking
        self.input_object = input_object
        self.value = value

    def message(self):
        return f"Input Field `{self.value}` removed from input type `{self.input_object}`"

    def path(self):
        return f"{self.input_object.name}.{self.value.name}"


class InputObjectTypeDescriptionChanged(Change):
    def __init__(self, input, name, new_field, old_field):
        self.input = input
        self.name = name
        self.new_field = new_field
        self.old_field = old_field

    def message(self):
        return (
            f"Description for Input field `{self.input.name}.{self.name}` "
            f"changed from `{self.old_field.description}` to `{self.new_field.description}`"
        )

    def path(self):
        return f"{self.input.name}.{self.name}"


class InputTypeDefaultChanged(Change):
    def __init__(self, input, name, new_field, old_field):
        self.input = input
        self.name = name
        self.new_field = new_field
        self.old_field = old_field

    def message(self):
        return (
            f"Default value for Input field `{self.input.name}.{self.name}` "
            f"changed from {self.old_field.default_value!r} to {self.new_field.default_value!r}"
        )

    def path(self):
        return f"{self.input.name}.{self.name}"


class InputObjectTypeTypeChanged(Change):
    def __init__(self, input, name, new_field, old_field):
        self.input = input
        self.name = name
        self.new_field = new_field
        self.old_field = old_field

    def message(self):
        return (
            f"`{self.input.name}.{self.name}` type changed from "
            f"`{self.old_field.type}` to `{self.new_field.type}`"
        )

    def path(self):
        return f"{self.input.name}.{self.name}"


#  ============== Arguments ==============


class AbstractArgumentChange(Change):
    def __init__(self, parent_type, field, arg_name, old_arg, new_arg):
        self.parent = parent_type
        self.field_name = field
        self.arg_name = arg_name
        self.old_arg = old_arg
        self.new_arg = new_arg

    def path(self):
        return f"{self.parent.name}.{self.field_name}"


class ArgumentDescriptionChanged(AbstractArgumentChange):
    def message(self):
        return (
            f"Description for argument `{self.arg_name}` on field `{self.parent}.{self.field_name}` "
            f"changed from `{self.old_arg.description}` to `{self.new_arg.description}`"
        )


class ArgumentDefaultValueChanged(AbstractArgumentChange):
    def message(self):
        return (
            f"Default value for argument `{self.arg_name}` on field `{self.parent}.{self.field_name}` "
            f"changed from `{self.old_arg.default_value!r}` to `{self.new_arg.default_value}`"
        )


class ArgumentTypeChanged(AbstractArgumentChange):
    def message(self):
        return (
            f"Type for argument `{self.arg_name}` on field `{self.parent}.{self.field_name}` "
            f"changed from `{self.old_arg.type}` to `{self.new_arg.type}`"
        )


class FieldArgumentAdded(Change):
    def __init__(self, parent, field_name, argument_name, arg_type):
        self.parent = parent
        self.field_name = field_name
        self.argument_name = argument_name
        self.arg_type = arg_type

    def message(self):
        return (
            f"Argument `{self.argument_name}: {self.arg_type.type}` "
            f"added to `{self.parent.name}.{self.field_name}`"
        )


class FieldArgumentRemoved(Change):
    def __init__(self, parent, field_name, argument_name):
        self.parent = parent
        self.field_name = field_name
        self.argument_name = argument_name

    def message(self):
        return (
            f"Removed argument `{self.argument_name}` from `{self.parent.name}.{self.field_name}`"
        )


#  ============== Interfaces ==============


class InterfaceFieldAdded(Change):
    def __init__(self, interface, field_name, field):
        self.interface = interface
        self.field_name = field_name
        self.field = field

    def message(self):
        return f"Field `{self.field_name}` of type `{self.field.type}` was added to interface `{self.interface}`"

    def path(self):
        return f"{self.interface.name}.{self.field_name}"


class InterfaceFieldRemoved(Change):
    def __init__(self, interface, field_name):
        self.interface = interface
        self.field_name = field_name

    def message(self):
        return f"Field `{self.field_name}` was removed from interface `{self.interface}`"

    def path(self):
        return f"{self.interface.name}.{self.field_name}"


class AbstractInterfanceChange(Change):
    def __init__(self, interface, field_name, old_field, new_field):
        self.interface = interface
        self.field_name = field_name
        self.old_field = old_field
        self.new_field = new_field

    def path(self):
        return f"{self.interface.name}.{self.field_name}"

    def message(self):
        raise NotImplementedError


class InterfaceFieldTypeChanged(AbstractInterfanceChange):
    def message(self):
        return (
            f"Field `{self.interface.name}.{self.field_name}` type "
            f"changed from `{self.old_field.type}` to `{self.new_field.type}`"
        )


class NewInterfaceImplemented(Change):
    def __init__(self, interface, field):
        self.interface = interface
        self.field = field

    def message(self):
        return f"`{self.field.name}` implements new interface `{self.interface.name}`"


class DroppedInterfaceImplementation(Change):
    def __init__(self, interface, field):
        self.interface = interface
        self.field = field

    def message(self):
        return f"`{self.field.name}` no longer implements interface `{self.interface.name}`"


class InterfaceFieldDescriptionChanged(AbstractInterfanceChange):
    def message(self):
        return (
            f"`{self.interface.name}.{self.field_name}` description changed "
            f"from `{self.old_field.description}` to `{self.new_field.description}`"
        )


class InterfaceFieldDeprecationReasonChanged(AbstractInterfanceChange):
    def message(self):
        return (
            f"`{self.interface.name}.{self.field_name}` deprecation reason changed "
            f"from `{self.old_field.deprecation_reason}` to `{self.new_field.deprecation_reason}`"
        )


#  ============== Object Type ==============


class ObjectTypeFieldAdded(Change):
    def __init__(self, parent, field_name):
        self.parent = parent
        self.field_name = field_name

    def message(self):
        return f"Field `{self.field_name}` was added to object type `{self.parent.name}`"

    def path(self):
        return f"{self.parent.name}.{self.field_name}"


class ObjectTypeFieldRemoved(Change):
    def __init__(self, parent, field_name):
        self.parent = parent
        self.field_name = field_name

    def message(self):
        return f"Field `{self.field_name}` was removed from object type `{self.parent.name}`"

    def path(self):
        return f"{self.parent.name}.{self.field_name}"


#  ============== Directives ==============


class AddedDirective(Change):
    def __init__(self, directive_name, directive_locations):
        self.directive_name = directive_name
        self.directive_locations = directive_locations

    def message(self):
        locations = ' | '.join(loc.name for loc in self.directive_locations)
        return f"Directive `{self.directive_name}` was added to use on `{locations}`"

    def path(self):
        return self.directive_name


class RemovedDirective(Change):
    def __init__(self, directive_name):
        self.directive_name = directive_name

    def message(self):
        return f"Directive `{self.directive_name}` was removed"

    def path(self):
        return self.directive_name


class DirectiveDescriptionChanged(Change):
    def __init__(self, old, new):
        self.old = old
        self.new = new

    def message(self):
        return (
            f"Description for directive `{self.new!s}` "
            f"changed from `{self.old.description}` to `{self.new.description}`"
        )


class DirectiveLocationsChanged(Change):
    def __init__(self, directive, old_locations, new_locations):
        self.directive = directive
        self.old_locations = old_locations
        self.new_locations = new_locations

    def message(self):
        return (
            f"Directive locations of `{self.directive!s}` changed "
            f"from `{' | '.join(l.name for l in self.old_locations)}` "
            f"to `{' | '.join(l.name for l in self.new_locations)}`"
        )

    def path(self):
        return self.directive.name


class DirectiveArgumentAdded(Change):
    def __init__(self, directive, arg_name, arg_type):
        self.directive = directive
        self.arg_name = arg_name
        self.arg_type = arg_type

    def message(self):
        return f"Added argument `{self.arg_name}: {self.arg_type.type}` to `{self.directive!s}` directive"


class DirectiveArgumentRemoved(Change):
    def __init__(self, directive, arg_name, arg_type):
        self.directive = directive
        self.arg_name = arg_name
        self.arg_type = arg_type

    def message(self):
        return f"Removed argument `{self.arg_name}: {self.arg_type.type}` from `{self.directive!s}` directive"

    def path(self):
        return self.directive.name


class DirectiveArgumentTypeChanged(Change):
    def __init__(self, directive, arg_name, old_type, new_type):
        self.directive = directive
        self.arg_name = arg_name
        self.old_type = old_type
        self.new_type = new_type

    def message(self):
        return (
            f"Type for argument `{self.arg_name}` on `{self.directive!s}` directive changed "
            f"from `{self.old_type!s}` to `{self.new_type!s}`"
        )

    def path(self):
        return self.directive.name


class DirectiveArgumentDefaultChanged(Change):
    def __init__(self, directive, arg_name, old_default, new_default):
        self.directive = directive
        self.arg_name = arg_name
        self.old_default = old_default
        self.new_default = new_default

    def message(self):
        return (
            f"Default value for argument `{self.arg_name}` on `{self.directive!s}` directive changed "
            f"from `{self.old_default!r}` to `{self.new_default!r}`"
        )

    def path(self):
        return self.directive.name


class DirectiveArgumentDescriptionChanged(Change):
    def __init__(self, directive, arg_name, old_desc, new_desc):
        self.directive = directive
        self.arg_name = arg_name
        self.old_desc = old_desc
        self.new_desc = new_desc

    def message(self):
        return (
            f"Description for argument `{self.arg_name}` on `{self.directive!s}` directive changed "
            f"from `{self.old_desc}` to `{self.new_desc}`"
        )

    def path(self):
        return self.directive.name
