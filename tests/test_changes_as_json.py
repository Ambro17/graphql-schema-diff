import json
from operator import itemgetter

from schemadiff.changes import Criticality, Change
from schemadiff.diff.schema import Schema
from schemadiff.formatting import json_dump_changes, changes_to_dict
from schemadiff.schema_loader import SchemaLoader as SchemaLoad
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
        },
        'checksum': 'be519517bbcc5dd41ff526719e0764ec',
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
        },
        'checksum': '6dde00418330279921218878d9ce7d38',
    }
    assert json.loads(the_change.to_json()) == expected_dict


def test_safe_change():
    class MyChange(Change):
        criticality = Criticality.safe('Hello')

        @property
        def message(self):
            return ''

        @property
        def path(self):
            return None

    the_change = MyChange()
    expected_dict = {
        'message': '',
        'path': None,
        'is_safe_change': True,
        'criticality': {
            'level': 'NON_BREAKING',
            'reason': 'Hello',
        },
        'checksum': 'd41d8cd98f00b204e9800998ecf8427e',
    }
    assert expected_dict == the_change.to_dict()
    assert json.loads(the_change.to_json()) == expected_dict


def test_json_dump_changes():
    old = SchemaLoad.from_file(TESTS_DATA / 'simple_schema.gql')
    new = SchemaLoad.from_file(TESTS_DATA / 'simple_schema_dangerous_and_breaking.gql')

    changes = Schema(old, new).diff()
    expected_changes = [
        {
            'criticality': {
                'level': 'NON_BREAKING',
                'reason': "This change won't break any preexisting query"
            },
            'is_safe_change': True,
            'message': 'Field `c` was added to object type `Query`',
            'path': 'Query.c',
            'checksum': '1e3b776bda2dd8b11804e7341bb8b2d1',
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
            'path': 'Query.a',
            'checksum': '5fba3d6ffc43c6769c6959ce5cb9b1c8',
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
            'path': 'Field.calculus',
            'checksum': '8890b911d44b2ead0dceeae066d98617',
        }
    ]

    changes_result = changes_to_dict(changes)
    by_path = itemgetter('path')
    assert sorted(changes_result, key=by_path) == sorted(expected_changes, key=by_path)

    # Assert the json dump has a 32-char checksum and the changes attributes as expected
    json_changes = json.loads(json_dump_changes(changes))
    assert all(len(change['checksum']) == 32 for change in json_changes)
    assert sorted(json_changes, key=by_path) == sorted(expected_changes, key=by_path)
