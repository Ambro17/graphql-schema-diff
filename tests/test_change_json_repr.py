import json
from operator import itemgetter

from schemadiff.changes import Criticality, Change
from schemadiff.diff.schema import Schema
from schemadiff.formatting import json_dump_changes, changes_to_dict
from schemadiff.graphql_schema import GraphQLSchema
from tests.test_schema_loading import TESTS_DATA


def test_dict_representation():
    class MyChange(Change):
        criticality = Criticality.breaking('If lorem is ipsum the world might end')

        @property
        def message(self):
            return 'Lorem should not be ipsum'

        @property
        def path(self):
            return 'Lorem.Ipsum'

    the_change = MyChange()
    expected_repr = {
        'message': 'Lorem should not be ipsum',
        'path': 'Lorem.Ipsum',
        'is_safe_change': False,
        'criticality': {
            'level': 'BREAKING',
            'reason': 'If lorem is ipsum the world might end',
        }
    }
    assert the_change.to_dict() == expected_repr


def test_json_representation():
    class MyChange(Change):
        criticality = Criticality.dangerous('This might be dangerous')

        @property
        def message(self):
            return 'Unagi'

        @property
        def path(self):
            return 'Unagi.Friends'

    the_change = MyChange()
    expected_dict = {
        'message': 'Unagi',
        'path': 'Unagi.Friends',
        'is_safe_change': False,
        'criticality': {
            'level': 'DANGEROUS',
            'reason': 'This might be dangerous',
        }
    }
    assert json.loads(the_change.to_json()) == expected_dict


def test_safe_change():
    class MyChange(Change):
        criticality = Criticality.safe('Hello')

        @property
        def message(self):
            return None

        @property
        def path(self):
            return ''

    the_change = MyChange()
    expected_dict = {
        'message': None,
        'path': '',
        'is_safe_change': True,
        'criticality': {
            'level': 'NON_BREAKING',
            'reason': 'Hello',
        }
    }
    assert expected_dict == the_change.to_dict()
    assert json.loads(the_change.to_json()) == expected_dict


def test_json_dump_changes():
    old = GraphQLSchema.from_file(TESTS_DATA / 'simple_schema.gql')
    new = GraphQLSchema.from_file(TESTS_DATA / 'simple_schema_dangerous_and_breaking.gql')

    changes = Schema(old, new).diff()
    changes_result = changes_to_dict(changes)

    expected_changes = [
        {
            'criticality': {
                'level': 'NON_BREAKING',
                'reason': "This change won't break any preexisting query"
            },
            'is_safe_change': True,
            'message': 'Field `c` was added to object type `Query`',
            'path': 'Query.c'
        },
        {
            'criticality': {
                'level': 'BREAKING',
                'reason': (
                    'Removing a field is a breaking change. It is preferred to deprecate the field before removing it.'
                )
            },
            'is_safe_change': False,
            'message': 'Field `a` was removed from object type `Query`',
            'path': 'Query.a'
        },
        {
            'criticality': {
                'level': 'DANGEROUS',
                'reason': (
                    'Changing the default value for an argument may '
                    'change the runtime behaviour of a field if it was never provided.'
                )
            },
            'is_safe_change': False,
            'message': 'Default value for argument `x` on field `Field.calculus` changed from `0` to `1`',
            'path': 'Field.calculus'
        }
    ]
    by_path = itemgetter('path')
    assert sorted(changes_result, key=by_path) == sorted(expected_changes, key=by_path)

    # Assert the json dump has a 32-char as keys and the values are the changes as dict
    dict_from_json = json.loads(json_dump_changes(changes))
    assert all(len(key) == 32 for key in dict_from_json.keys())
    values = dict_from_json.values()
    assert sorted(values, key=by_path) == sorted(expected_changes, key=by_path)
