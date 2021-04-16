import pytest
from graphql import build_schema as schema

from schemadiff.changes import Change, Criticality
from schemadiff.changes.field import FieldArgumentAdded
from schemadiff.changes.object import ObjectTypeFieldAdded
from schemadiff.validation import validate_changes
from schemadiff.validation_rules import (
    ValidationRule,
    AddFieldWithoutDescription,
    AddTypeWithoutDescription,
    AddEnumValueWithoutDescription,
    RemoveEnumValueDescription,
    RemoveTypeDescription,
)
from schemadiff.diff.schema import Schema


@pytest.mark.parametrize('rule', ValidationRule.__subclasses__())
def test_is_valid_defaults_to_true_for_any_other_change(rule):
    class UnexpectedChange(Change):
        criticality = Criticality.safe()

        @property
        def message(self):
            return ""

        @property
        def path(self):
            return ""

    assert rule(UnexpectedChange()).is_valid() is True


def test_type_added_with_desc():
    a = schema('''
    type MyType{
        a: Int
    }
    ''')
    b = schema('''
    type MyType{
        a: Int
    }
    """This has desc"""
    type NewType{
        """And its field also has a desc"""
        b: String!
    }
    ''')
    diff = Schema(a, b).diff()
    assert AddTypeWithoutDescription(diff[0]).is_valid() is True


def test_type_added_with_desc_but_missing_desc_on_its_fields():
    a = schema('''
    type MyType{
        a: Int
    }
    ''')
    b = schema('''
    type MyType{
        a: Int
    }
    """This has desc"""
    type NewType{
        """This one has desc"""
        b: String!
        c: Int!
    }
    ''')
    diff = Schema(a, b).diff()
    assert AddTypeWithoutDescription(diff[0]).is_valid() is False
    assert AddTypeWithoutDescription(diff[0]).message == (
        'Type `NewType` was added without a description for NewType (rule: '
        '`add-type-without-description`).'
    )


def test_type_added_without_desc():
    a = schema('''
    type MyType{
        a: Int
    }
    ''')
    b = schema('''
    type MyType{
        a: Int
    }
    type NewType{
        b: String!
    }
    ''')
    diff = Schema(a, b).diff()
    assert AddTypeWithoutDescription(diff[0]).is_valid() is False


def test_type_changed_desc_removed():
    a = schema('''
    """This has desc"""
    type MyType{
        a: Int
    }
    ''')
    b = schema('''
    type MyType{
        a: Int
    }
    ''')
    c = schema('''
    """"""
    type MyType{
        a: Int
    }
    ''')
    diff = Schema(a, b).diff()
    assert RemoveTypeDescription(diff[0]).is_valid() is False

    diff = Schema(a, c).diff()
    assert RemoveTypeDescription(diff[0]).is_valid() is False


def test_field_added_without_desc():
    a = schema('''
    type MyType{
        a: Int
    }
    ''')
    b = schema('''
    type MyType{
        a: Int
        b: String!
    }
    ''')
    c = schema('''
    type MyType{
        a: Int
        """WithDesc"""
        b: String!
    }
    ''')
    diff = Schema(a, b).diff()
    assert AddFieldWithoutDescription(diff[0]).is_valid() is False

    diff = Schema(a, c).diff()
    assert AddFieldWithoutDescription(diff[0]).is_valid() is True


def test_enum_added_without_desc():
    a = schema('''
    enum Letters {
        A
    }
    ''')
    b = schema('''
    enum Letters {
        A
        B
    }
    ''')
    c = schema('''
    enum Letters {
        A
        """WithDesc"""
        B
    }
    ''')
    diff = Schema(a, b).diff()
    assert AddEnumValueWithoutDescription(diff[0]).is_valid() is False

    diff = Schema(a, c).diff()
    assert AddEnumValueWithoutDescription(diff[0]).is_valid() is True


def test_enum_value_removing_desc():
    a = schema('''
    enum Letters {
        """WithDesc"""
        A
    }
    ''')
    b = schema('''
    enum Letters {
        A
    }
    ''')
    diff = Schema(a, b).diff()
    assert RemoveEnumValueDescription(diff[0]).is_valid() is False


def test_schema_added_field_no_desc():

    schema_restrictions = ['add-field-without-description']

    old_schema = schema("""
    schema {
        query: Query
    }

    type Query {
        field: String!
    }

    type AddedType {
        added: Int
    }
    """)
    new_schema = schema("""
    schema {
        query: Query
    }

    type Query {
        field: String!
    }

    type AddedType {
        added: Int
        other: Int
    }
    """)
    diff = Schema(old_schema, new_schema).diff()
    # Type Int was also added but its ignored because its a primitive.
    assert diff and len(diff) == 1
    error_msg = (
        'Field `other` was added to object type `AddedType` without a description for AddedType.other '
        '(rule: `add-field-without-description`).'
    )
    result =  validate_changes(diff, schema_restrictions)
    assert result.ok is False
    assert result.errors and len(result.errors) == 1
    assert result.errors[0].reason == error_msg
    assert diff[0].path == 'AddedType.other'
    assert result.errors[0].change.path == 'AddedType.other'
    assert result.errors[0].rule == 'add-field-without-description'


# Register the new validation rule for the following two tests
class FieldHasTooManyArguments(ValidationRule):
    """Restrict adding fields with too many top level arguments"""

    name = "field-has-too-many-arguments"
    limit = 10

    def is_valid(self) -> bool:
        if not isinstance(self.change, (ObjectTypeFieldAdded, FieldArgumentAdded)):
            return True

        if len(self.args) > self.limit:
            return False
        else:
            return True

    @property
    def args(self):
        return self.change.field.args or {}

    @property
    def message(self):
        return f"Field `{self.change.parent.name}.{self.change.field_name}` has too many arguments " \
               f"({len(self.args)}>{self.limit}). Rule: {self.name}"


def test_cant_create_mutation_with_more_than_10_arguments():
    schema_restrictions = [FieldHasTooManyArguments.name]

    old_schema = schema("""
    schema {
        mutation: Mutation
    }

    type Mutation {
        field: Int
    }
    """)

    new_schema = schema("""
    schema {
        mutation: Mutation
    }

    type Mutation {
        field: Int
        mutation_with_too_many_args(
            a1: Int, a2: Int, a3: Int, a4: Int, a5: Int, a6: Int, a7: Int, a8: Int, a9: Int, a10: Int, a11: Int 
        ): Int
    }
    """)

    diff = Schema(old_schema, new_schema).diff()
    # Type Int was also added but its ignored because its a primitive.
    assert diff and len(diff) == 1
    error_msg = (
        'Field `Mutation.mutation_with_too_many_args` has too many arguments (11>10). '
        'Rule: field-has-too-many-arguments'
    )
    result =  validate_changes(diff, schema_restrictions)
    assert result.ok is False
    assert result.errors and len(result.errors) == 1
    assert result.errors[0].reason == error_msg
    assert result.errors[0].change.path == 'Mutation.mutation_with_too_many_args'
    assert result.errors[0].rule == FieldHasTooManyArguments.name


def test_cant_add_arguments_to_mutation_if_exceeds_10_args():
    schema_restrictions = [FieldHasTooManyArguments.name]

    old_schema = schema("""
    schema {
        mutation: Mutation
    }

    type Mutation {
        field: Int
        mutation_with_too_many_args(
            a1: Int, a2: Int, a3: Int, a4: Int, a5: Int, a6: Int, a7: Int, a8: Int, a9: Int, a10: Int 
        ): Int
    }
    """)

    new_schema = schema("""
    schema {
        mutation: Mutation
    }

    type Mutation {
        field: Int
        mutation_with_too_many_args(
            a1: Int, a2: Int, a3: Int, a4: Int, a5: Int, a6: Int, a7: Int, a8: Int, a9: Int, a10: Int, a11: Int 
        ): Int
    }
    """)

    diff = Schema(old_schema, new_schema).diff()
    # Type Int was also added but its ignored because its a primitive.
    assert diff and len(diff) == 1
    error_msg = (
        'Field `Mutation.mutation_with_too_many_args` has too many arguments (11>10). '
        'Rule: field-has-too-many-arguments'
    )
    result =  validate_changes(diff, schema_restrictions)
    assert result.ok is False
    assert result.errors and len(result.errors) == 1
    assert result.errors[0].reason == error_msg
    assert result.errors[0].change.message == "Argument `a11: Int` added to `Mutation.mutation_with_too_many_args`"
    assert result.errors[0].change.checksum() == "221964c2ab5bbc6bd1ed19bcd8d69e70"
    assert result.errors[0].rule == FieldHasTooManyArguments.name

    assert diff[0].path == 'Mutation.mutation_with_too_many_args'


def test_can_allow_rule_infractions():
    CHANGE_ID = '221964c2ab5bbc6bd1ed19bcd8d69e70'
    validation_rules = [FieldHasTooManyArguments.name]

    old_schema = schema("""
    schema {
        mutation: Mutation
    }

    type Mutation {
        field: Int
        mutation_with_too_many_args(
            a1: Int, a2: Int, a3: Int, a4: Int, a5: Int, a6: Int, a7: Int, a8: Int, a9: Int, a10: Int 
        ): Int
    }
    """)

    new_schema = schema("""
    schema {
        mutation: Mutation
    }

    type Mutation {
        field: Int
        mutation_with_too_many_args(
            a1: Int, a2: Int, a3: Int, a4: Int, a5: Int, a6: Int, a7: Int, a8: Int, a9: Int, a10: Int, a11: Int 
        ): Int
    }
    """)

    changes = Schema(old_schema, new_schema).diff()
    result = validate_changes(changes, validation_rules)
    assert result.ok is False
    assert result.errors[0].change.checksum() == CHANGE_ID
    result = validate_changes(changes, validation_rules, allowed_changes={CHANGE_ID})
    assert result.ok is True
    assert result.errors == []
