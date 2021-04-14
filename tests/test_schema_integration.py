from pathlib import Path

from schemadiff.schema_loader import SchemaLoader
from schemadiff.diff.schema import Schema

TESTS_DATA = Path(__file__).parent / 'data'


def test_compare_from_schema_string_sdl():
    old_schema = SchemaLoader.from_file(TESTS_DATA / 'old_schema.gql')
    new_schema = SchemaLoader.from_file(TESTS_DATA / 'new_schema.gql')

    diff = Schema(old_schema, new_schema).diff()
    assert len(diff) == 38

    expected_changes = {
         'Argument `arg: Int` added to `CType.a`',
         "Default value for argument `anotherArg` on `@yolo` directive changed from `Undefined` to `'Test'`",
         'Default value for argument `arg` on field `CType.d` changed from `Undefined` to `10`',
         'Default value for argument `arg` on field `WithArguments.b` changed from `1` to `2`',
         "Default value for input field `AInput.a` changed from `'1'` to `1`",
         'Deprecation reason for enum value `F` changed from `Old` to `New`',
         'Deprecation reason on field `CType.a` changed from `whynot` to `cuz`',
         'Description for Input field `AInput.a` changed from `a` to `None`',
         'Description for argument `a` on field `WithArguments.a` changed from `Meh` to `None`',
         'Description for argument `someArg` on `@yolo` directive changed from `Included when true.` to `None`',
         'Description for directive `@yolo` changed from `Old` to `None`',
         'Description for type `Query` changed from `The Query Root of this schema` to `None`',
         'Directive `@willBeRemoved` was removed',
         'Directive `@yolo2` was added to use on `FIELD`',
         (
            'Directive locations of `@yolo` changed from `FIELD | FRAGMENT_SPREAD | INLINE_FRAGMENT` '
            'to `FIELD | FIELD_DEFINITION`'
         ),
         'Enum value `C` was removed from `Options` enum',
         'Enum value `D` was added to `Options` enum',
         'Enum value `E` was deprecated with reason `No longer supported`',
         'Field `anotherInterfaceField` was removed from interface `AnotherInterface`',
         'Field `b` of type `Int` was added to interface `AnotherInterface`',
         'Field `b` was added to object type `CType`',
         'Field `c` was removed from object type `CType`',
         'Input Field `b` removed from input type `AInput`',
         'Input Field `c: String!` was added to input type `AInput`',
         'Removed argument `anArg` from `Query.a`',
         'Removed argument `willBeRemoved: Boolean!` from `@yolo` directive',
         'Type `DType` was added',
         'Type `WillBeRemoved` was removed',
         'Type for argument `b` on field `WithArguments.a` changed from `String` to `String!`',
         'Type for argument `someArg` on `@yolo` directive changed from `Boolean!` to `String!`',
         'Union member `BType` was removed from `MyUnion` Union type',
         'Union member `DType` was added to `MyUnion` Union type',
         '`AInput.a` type changed from `String` to `Int`',
         '`BType` kind changed from `OBJECT` to `INPUT OBJECT`',
         '`CType` implements new interface `AnInterface`',
         '`Query.a` description changed from `Just a simple string` to `None`',
         '`Query.b` type changed from `BType` to `Int!`',
         '`WithInterfaces` no longer implements interface `AnotherInterface`'
    }
    messages = [change.message for change in diff]
    for message in messages:
        assert message in expected_changes, f"{message} not found on expected messages"
