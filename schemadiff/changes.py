from abc import abstractmethod, ABC
from enum import Enum

from attr import dataclass
from graphql import is_wrapping_type, is_non_null_type, is_list_type


class Criticality(Enum):
    NonBreaking = 'NON_BREAKING'
    Dangerous = 'DANGEROUS'
    Breaking = 'BREAKING'


@dataclass
class ApiChange:
    level: Criticality
    reason: str

    @classmethod
    def breaking(cls, reason):
        return cls(level=Criticality.Breaking, reason=reason)

    @classmethod
    def dangerous(cls, reason):
        return cls(level=Criticality.Dangerous, reason=reason)

    @classmethod
    def safe(cls, reason="This change won't break any preexisting query"):
        return cls(level=Criticality.NonBreaking, reason=reason)


def is_safe_type_change(old_type, new_type) -> bool:
    """Depending on the old an new type, a field type change may be breaking, dangerous or safe

    * If both fields are 'leafs' in the sense they don't wrap an inner type, just compare their type.
    * If the new type has a non-null constraint, check that it was already non-null and compare against the contained
      type. If the contraint is new, just compare with old_type
    * If the old type is a list and the new one too, compare their inner types
      If the new type has a non-null constraint, compare against the wrapped type
    """
    if not is_wrapping_type(old_type) and not is_wrapping_type(new_type):
        return str(old_type) == str(new_type)
    if is_non_null_type(new_type):
        # Grab the inner type it it also was non null.
        of_type = old_type.of_type if is_non_null_type(old_type) else old_type
        return is_safe_type_change(of_type, new_type.of_type)

    if is_list_type(old_type):
        # If both types are lists, compare their inner type.
        # If the new type has a non-null constraint, compare with its inner type (may be a list or not)
        return (
            (
                    is_list_type(new_type) and is_safe_type_change(old_type.of_type, new_type.of_type)
            )
            or
            (
                    is_non_null_type(new_type) and is_safe_type_change(old_type, new_type.of_type)
            )
        )

    return False


def is_safe_change_for_input_value(old_type, new_type):
    if not is_wrapping_type(old_type) and not is_wrapping_type(new_type):
        return str(old_type) == str(new_type)
    if is_list_type(old_type) and is_list_type(new_type):
        return is_safe_change_for_input_value(old_type.of_type, new_type.of_type)

    if is_non_null_type(old_type):
        # Grab the inner type it it also was non null.
        of_type = new_type.of_type if is_non_null_type(new_type) else new_type
        return is_safe_type_change(old_type.of_type, of_type)

    return False


class Change(ABC):

    criticality: ApiChange

    @property
    def breaking(self):
        return self.criticality.level == Criticality.Breaking

    @property
    def dangerous(self):
        return self.criticality.level == Criticality.Dangerous

    @property
    def safe(self):
        return self.criticality.level == Criticality.NonBreaking

    @property
    @abstractmethod
    def message(self):
        """Formatted change message"""

    @property
    @abstractmethod
    def path(self):
        """Path to the affected schema member"""


class RemovedType(Change):

    criticality = ApiChange.breaking(
        "Removing a type is a breaking change. "
        "It is preferable to deprecate and remove all references to this type first."
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

    criticality = ApiChange.safe()

    def __init__(self, added_type):
        self.type = added_type

    @property
    def message(self):
        return f"Type `{self.type.name}` was added"

    @property
    def path(self):
        return f'{self.type.name}'


class TypeDescriptionChanged(Change):

    criticality = ApiChange.safe()

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
    criticality = ApiChange.breaking(
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


class FieldDescriptionChanged(Change):

    criticality = ApiChange.safe()

    def __init__(self, new_type, name, old_field, new_field):
        self.criticality = Criticality.NonBreaking
        self.type = new_type
        self.field_name = name
        self.old_field = old_field
        self.new_field = new_field

    @property
    def message(self):
        return (
            f"`{self.type.name}.{self.field_name}` description changed"
            f" from `{self.old_field.description}` to `{self.new_field.description}`"
        )

    @property
    def path(self):
        return f'{self.type}.{self.field_name}'


class FieldDeprecationReasonChanged(Change):

    criticality = ApiChange.safe()

    def __init__(self, type, name, old_field, new_field):
        self.type = type
        self.field_name = name
        self.old_field = old_field
        self.new_field = new_field

    @property
    def message(self):
        return (
            f"Deprecation reason on field `{self.type}.{self.field_name}` changed "
            f"from `{self.old_field.deprecation_reason}` to `{self.new_field.deprecation_reason}`"
        )

    @property
    def path(self):
        return f"{self.type}.{self.field_name}"


class FieldTypeChanged(Change):

    def __init__(self, type, field_name, old_field, new_field):
        self.criticality = ApiChange.safe() \
                           if is_safe_type_change(old_field, new_field)\
                           else ApiChange.breaking(reason="This type change may break existing queries")
        self.type = type
        self.field_name = field_name
        self.old_field = old_field
        self.new_field = new_field

    @property
    def message(self):
        return (
            f"`{self.type}.{self.field_name}` type changed "
            f"from `{self.old_field.type}` to `{self.new_field.type}`"
        )

    @property
    def path(self):
        return f"{self.type}.{self.field_name}"


#  ============== ENUMS ==============


class EnumValueAdded(Change):
    def __init__(self, enum, value):
        self.criticality = ApiChange.dangerous(
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
        self.criticality = ApiChange.breaking(
            "Removing an enum value will break existing queries that use this enum value"
        )
        self.enum = enum
        self.value = value

    @property
    def message(self):
        return f"Enum value `{self.value}` was removed from `{self.enum.name}` enum"

    @property
    def path(self):
        return f"{self.enum.name}.{self.value}"


class EnumValueDescriptionChanged(Change):

    criticality = ApiChange.safe()

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

    criticality = ApiChange.safe()

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


#  ============== Union ==============

class UnionMemberAdded(Change):

    criticality = ApiChange.dangerous(
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

    criticality = ApiChange.breaking(
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


#  ============== Input Objects ==============


class InputFieldAdded(Change):

    BREAKING_MSG = (
        "Adding a non-null field to an existing input type will cause existing "
        "queries that use this input type to break because they will "
        "not provide a value for this new field."
    )

    def __init__(self, input_object, field_name, field):
        self.criticality = (
            ApiChange.safe()
            if is_non_null_type(field.type) is False
            else ApiChange.breaking(self.BREAKING_MSG)
        )

        self.input_object = input_object
        self.field_name = field_name
        self.field = field

    @property
    def message(self):
        return f"Input Field `{self.field_name}: {self.field.type}` was added to input type `{self.input_object}`"

    @property
    def path(self):
        return f"{self.input_object}.{self.field_name}"


class InputFieldRemoved(Change):

    criticality = ApiChange.breaking(
        'Removing an input field will break queries that use this input field.'
    )

    def __init__(self, input_object, value):
        self.input_object = input_object
        self.value = value

    @property
    def message(self):
        return f"Input Field `{self.value}` removed from input type `{self.input_object}`"

    @property
    def path(self):
        return f"{self.input_object}.{self.value}"


class InputFieldDescriptionChanged(Change):

    criticality = ApiChange.safe()

    def __init__(self, input, name, new_field, old_field):
        self.input = input
        self.name = name
        self.new_field = new_field
        self.old_field = old_field

    @property
    def message(self):
        return (
            f"Description for Input field `{self.input.name}.{self.name}` "
            f"changed from `{self.old_field.description}` to `{self.new_field.description}`"
        )

    @property
    def path(self):
        return f"{self.input.name}.{self.name}"


class InputFieldDefaultChanged(Change):

    criticality = ApiChange.dangerous(
        "Changing the default value for an argument may change the runtime "
        "behaviour of a field if it was never provided."
    )

    def __init__(self, input, name, new_field, old_field):
        self.input = input
        self.name = name
        self.new_field = new_field
        self.old_field = old_field

    @property
    def message(self):
        return (
            f"Default value for input field `{self.input.name}.{self.name}` "
            f"changed from `{self.old_field.default_value!r}` to `{self.new_field.default_value!r}`"
        )

    @property
    def path(self):
        return f"{self.input.name}.{self.name}"


class InputFieldTypeChanged(Change):
    def __init__(self, input, name, new_field, old_field):
        self.criticality = (
            ApiChange.safe()
            if is_safe_change_for_input_value(old_field, new_field)
            else ApiChange.breaking(
                "Changing the type of an input field can break existing queries that use this field"
            )
        )
        self.input = input
        self.name = name
        self.new_field = new_field
        self.old_field = old_field

    @property
    def message(self):
        return (
            f"`{self.input.name}.{self.name}` type changed from "
            f"`{self.old_field.type}` to `{self.new_field.type}`"
        )

    @property
    def path(self):
        return f"{self.input.name}.{self.name}"


#  ============== Arguments ==============


class FieldAbstractArgumentChange(Change):
    def __init__(self, parent_type, field, arg_name, old_arg, new_arg):
        self.parent = parent_type
        self.field_name = field
        self.arg_name = arg_name
        self.old_arg = old_arg
        self.new_arg = new_arg

    @property
    def path(self):
        return f"{self.parent.name}.{self.field_name}"


class FieldArgumentDescriptionChanged(FieldAbstractArgumentChange):

    criticality = ApiChange.safe()

    @property
    def message(self):
        return (
            f"Description for argument `{self.arg_name}` on field `{self.parent}.{self.field_name}` "
            f"changed from `{self.old_arg.description}` to `{self.new_arg.description}`"
        )


class FieldArgumentDefaultValueChanged(FieldAbstractArgumentChange):
    criticality = ApiChange.dangerous(
        "Changing the default value for an argument may change the runtime "
        "behaviour of a field if it was never provided."
    )

    @property
    def message(self):
        return (
            f"Default value for argument `{self.arg_name}` on field `{self.parent}.{self.field_name}` "
            f"changed from `{self.old_arg.default_value!r}` to `{self.new_arg.default_value!r}`"
        )


class FieldArgumentTypeChanged(FieldAbstractArgumentChange):

    def __init__(self, parent_type, field, arg_name, old_arg, new_arg):
        super().__init__(parent_type, field, arg_name, old_arg, new_arg)
        self.criticality = (
                ApiChange.safe()
                if is_safe_change_for_input_value(old_arg.type, new_arg.type)
                else ApiChange.breaking(
                    "Changing the type of a field's argument can break existing queries that use this argument."
                )
        )

    @property
    def message(self):
        return (
            f"Type for argument `{self.arg_name}` on field `{self.parent}.{self.field_name}` "
            f"changed from `{self.old_arg.type}` to `{self.new_arg.type}`"
        )


class FieldArgumentAdded(Change):
    def __init__(self, parent, field_name, argument_name, arg_type):
        self.criticality = ApiChange.safe() if not is_non_null_type(arg_type.type) else ApiChange.breaking(
            "Adding a required argument to an existing field is a breaking "
            "change because it will break existing uses of this field"
        )
        self.parent = parent
        self.field_name = field_name
        self.argument_name = argument_name
        self.arg_type = arg_type


    @property
    def message(self):
        return (
            f"Argument `{self.argument_name}: {self.arg_type.type}` "
            f"added to `{self.parent.name}.{self.field_name}`"
        )

    @property
    def path(self):
        return f"{self.parent}.{self.field_name}"


class FieldArgumentRemoved(Change):

    criticality = ApiChange.breaking(
        "Removing a field argument will break queries that use this argument"
    )

    def __init__(self, parent, field_name, argument_name):
        self.parent = parent
        self.field_name = field_name
        self.argument_name = argument_name

    @property
    def message(self):
        return (
            f"Removed argument `{self.argument_name}` from `{self.parent.name}.{self.field_name}`"
        )

    @property
    def path(self):
        return f"{self.parent}.{self.field_name}"

#  ============== Interfaces ==============


class InterfaceFieldAdded(Change):

    criticality = ApiChange.dangerous(
        "Adding an interface to an object type may break existing clients " 
        "that were not programming defensively against a new possible type."
    )

    def __init__(self, interface, field_name, field):
        self.interface = interface
        self.field_name = field_name
        self.field = field

    @property
    def message(self):
        return f"Field `{self.field_name}` of type `{self.field.type}` was added to interface `{self.interface}`"

    @property
    def path(self):
        return f"{self.interface.name}.{self.field_name}"


class InterfaceFieldRemoved(Change):

    criticality = ApiChange.dangerous(
        "Removing an interface from an object type can break existing "
        "queries that use this in a fragment spread."
    )

    def __init__(self, interface, field_name):
        self.interface = interface
        self.field_name = field_name

    @property
    def message(self):
        return f"Field `{self.field_name}` was removed from interface `{self.interface}`"

    @property
    def path(self):
        return f"{self.interface.name}.{self.field_name}"


class AbstractInterfanceChange(Change):
    def __init__(self, interface, field_name, old_field, new_field):
        self.interface = interface
        self.field_name = field_name
        self.old_field = old_field
        self.new_field = new_field

    @property
    def path(self):
        return f"{self.interface.name}.{self.field_name}"


class InterfaceFieldTypeChanged(AbstractInterfanceChange):

    @property
    def message(self):
        return (
            f"Field `{self.interface.name}.{self.field_name}` type "
            f"changed from `{self.old_field.type}` to `{self.new_field.type}`"
        )


class NewInterfaceImplemented(Change):

    criticality = ApiChange.dangerous(
        "Adding an interface to an object type may break existing clients "
        "that were not programming defensively against a new possible type."
    )

    def __init__(self, interface, type):
        self.interface = interface
        self.type = type

    @property
    def message(self):
        return f"`{self.type.name}` implements new interface `{self.interface.name}`"

    @property
    def path(self):
        return f"{self.type}"


class DroppedInterfaceImplementation(Change):

    criticality = ApiChange.breaking(
        "Removing an interface from an object type can break existing queries "
        "that use this in a fragment spread."
    )

    def __init__(self, interface, type):
        self.interface = interface
        self.type = type

    @property
    def message(self):
        return f"`{self.type.name}` no longer implements interface `{self.interface.name}`"

    @property
    def path(self):
        return f"{self.type}"


class InterfaceFieldDescriptionChanged(AbstractInterfanceChange):
    criticality = Criticality.NonBreaking

    @property
    def message(self):
        return (
            f"`{self.interface.name}.{self.field_name}` description changed "
            f"from `{self.old_field.description}` to `{self.new_field.description}`"
        )


class InterfaceFieldDeprecationReasonChanged(AbstractInterfanceChange):
    criticality = Criticality.NonBreaking

    @property
    def message(self):
        return (
            f"`{self.interface.name}.{self.field_name}` deprecation reason changed "
            f"from `{self.old_field.deprecation_reason}` to `{self.new_field.deprecation_reason}`"
        )


#  ============== Object Type ==============


class ObjectTypeFieldAdded(Change):

    criticality = ApiChange.safe()

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
            ApiChange.dangerous(
                "Removing deprecated fields without sufficient time for clients "
                "to update their queries may break their code"
            ) if field.deprecation_reason else ApiChange.breaking(
                "Removing a field is a breaking change. It is preferable to deprecate the field before removing it."
            )
        )

    @property
    def message(self):
        return f"Field `{self.field_name}` was removed from object type `{self.parent.name}`"

    @property
    def path(self):
        return f"{self.parent.name}.{self.field_name}"


#  ============== Directives ==============


class DirectiveChange(Change):

    @property
    def path(self):
        return f"{self.directive}"


class AddedDirective(DirectiveChange):

    criticality = ApiChange.safe()

    def __init__(self, directive, directive_locations):
        self.directive = directive
        self.directive_locations = directive_locations

    @property
    def message(self):
        locations = ' | '.join(loc.name for loc in self.directive_locations)
        return f"Directive `{self.directive}` was added to use on `{locations}`"


class RemovedDirective(DirectiveChange):

    criticality = ApiChange.breaking("Removing a directive may break clients that depend on them.")

    def __init__(self, directive):
        self.directive = directive

    @property
    def message(self):
        return f"Directive `{self.directive}` was removed"


class DirectiveDescriptionChanged(DirectiveChange):
    criticality = ApiChange.safe()

    def __init__(self, old, new):
        self.old = old
        self.new = new

    @property
    def message(self):
        return (
            f"Description for directive `{self.new!s}` "
            f"changed from `{self.old.description}` to `{self.new.description}`"
        )

    @property
    def path(self):
        return f"{self.new}"


class DirectiveLocationsChanged(DirectiveChange):
    def __init__(self, directive, old_locations, new_locations):
        self.directive = directive
        self.old_locations = old_locations
        self.new_locations = new_locations
        self.criticality = (
            ApiChange.safe() if self._only_additions() else ApiChange.breaking(
                "Removing a directive location will break any instance of its usage. "
                "Be sure no one uses it before removing it"
            )
        )

    def _only_additions(self):
        new_location_names = {l.name for l in self.new_locations}
        return all(l.name in new_location_names for l in self.old_locations)

    @property
    def message(self):
        return (
            f"Directive locations of `{self.directive!s}` changed "
            f"from `{' | '.join(l.name for l in self.old_locations)}` "
            f"to `{' | '.join(l.name for l in self.new_locations)}`"
        )


class DirectiveArgumentAdded(DirectiveChange):
    def __init__(self, directive, arg_name, arg_type):
        self.criticality = ApiChange.safe() if not is_non_null_type(arg_type.type) else ApiChange.breaking(
            "Adding a non nullable directive argument will break existing usages of the directive"
        )
        self.directive = directive
        self.arg_name = arg_name
        self.arg_type = arg_type

    @property
    def message(self):
        return f"Added argument `{self.arg_name}: {self.arg_type.type}` to `{self.directive!s}` directive"


class DirectiveArgumentRemoved(DirectiveChange):

    criticality = ApiChange.breaking("Removing a directive argument will break existing usages of the argument")

    def __init__(self, directive, arg_name, arg_type):
        self.directive = directive
        self.arg_name = arg_name
        self.arg_type = arg_type

    @property
    def message(self):
        return f"Removed argument `{self.arg_name}: {self.arg_type.type}` from `{self.directive!s}` directive"


class DirectiveArgumentTypeChanged(DirectiveChange):
    def __init__(self, directive, arg_name, old_type, new_type):
        self.criticality = (
            ApiChange.breaking("Changing the argument type is a breaking change")
            if not is_safe_change_for_input_value(old_type, new_type)
            else ApiChange.safe("Changing an input field from non-null to null is considered non-breaking")
        )
        self.directive = directive
        self.arg_name = arg_name
        self.old_type = old_type
        self.new_type = new_type

    @property
    def message(self):
        return (
            f"Type for argument `{self.arg_name}` on `{self.directive!s}` directive changed "
            f"from `{self.old_type}` to `{self.new_type}`"
        )


class DirectiveArgumentDefaultChanged(DirectiveChange):
    def __init__(self, directive, arg_name, old_default, new_default):
        self.criticality = ApiChange.dangerous(
            "Changing the default value for an argument may change the runtime "
            "behaviour of a field if it was never provided."
          )
        self.directive = directive
        self.arg_name = arg_name
        self.old_default = old_default
        self.new_default = new_default

    @property
    def message(self):
        return (
            f"Default value for argument `{self.arg_name}` on `{self.directive!s}` directive changed "
            f"from `{self.old_default!r}` to `{self.new_default!r}`"
        )


class DirectiveArgumentDescriptionChanged(DirectiveChange):
    criticality = ApiChange.safe()

    def __init__(self, directive, arg_name, old_desc, new_desc):
        self.directive = directive
        self.arg_name = arg_name
        self.old_desc = old_desc
        self.new_desc = new_desc

    @property
    def message(self):
        return (
            f"Description for argument `{self.arg_name}` on `{self.directive!s}` directive changed "
            f"from `{self.old_desc}` to `{self.new_desc}`"
        )
