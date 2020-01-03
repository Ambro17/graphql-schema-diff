import hashlib
import json

from schemadiff.diff.schema import Schema
from schemadiff.graphql_schema import GraphQLSchema
from schemadiff.formatting import print_diff, print_json
from tests.test_schema_loading import TESTS_DATA


def test_print_diff_shows_difference(capsys):
    old_schema = GraphQLSchema.from_file(TESTS_DATA / 'simple_schema.gql')
    new_schema = GraphQLSchema.from_file(TESTS_DATA / 'simple_schema_breaking_changes.gql')

    diff = Schema(old_schema, new_schema).diff()
    assert len(diff) == 1
    ret = print_diff(diff)
    assert ret is None
    assert capsys.readouterr().out == (
        '❌ Field `a` was removed from object type `Query`\n'
    )


def test_print_json_shows_difference(capsys):
    old_schema = GraphQLSchema.from_file(TESTS_DATA / 'simple_schema.gql')
    new_schema = GraphQLSchema.from_file(TESTS_DATA / 'simple_schema_breaking_changes.gql')

    diff = Schema(old_schema, new_schema).diff()
    assert len(diff) == 1
    print_json(diff)
    json_output = capsys.readouterr().out
    output_as_dict = json.loads(json_output)
    change_message = "Field `a` was removed from object type `Query`"
    assert output_as_dict == {
        "5fba3d6ffc43c6769c6959ce5cb9b1c8": {
            "message": change_message,
            "path": "Query.a",
            "is_safe_change": False,
            "criticality": {
                "level": "BREAKING",
                "reason": "Removing a field is a breaking change. "
                          "It is preferred to deprecate the field before removing it."
            }
        }
    }
    # Assert the diff key is the md5 checksum of the change message
    assert tuple(output_as_dict.keys())[0] == hashlib.md5(change_message.encode('utf-8')).hexdigest()

