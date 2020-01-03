import json
import sys
from unittest.mock import patch

import pytest

from schemadiff.__main__ import main, parse_args, cli


def test_no_diff(capsys):
    SCHEMA_FILE = 'tests/data/simple_schema.gql'
    args = parse_args([
        '-o', SCHEMA_FILE,
        '-n', SCHEMA_FILE,
    ])
    exit_code = main(args)
    stdout = capsys.readouterr()
    assert exit_code == 0
    assert stdout.out == '🎉 Both schemas are equal!\n'
    assert stdout.err == ''


def test_schema_path_not_found(capsys):
    SCHEMA_FILE = 'tests/data/not_a_path.gql'
    with pytest.raises(SystemExit):
        parse_args([
            '-o', SCHEMA_FILE,
            '-n', SCHEMA_FILE,
        ])
    assert "No such file or directory: 'tests/data/not_a_path.gql'" in capsys.readouterr().err


def test_schema_default_mode(capsys):
    SCHEMA_FILE = 'tests/data/simple_schema.gql'
    ANOTHER_SCHEMA_FILE = 'tests/data/simple_schema_dangerous_changes.gql'
    args = parse_args([
        '--old-schema', SCHEMA_FILE,
        '--new-schema', ANOTHER_SCHEMA_FILE,
    ])
    exit_code = main(args)
    assert exit_code == 0

    stdout = capsys.readouterr()
    assert "✔️ Field `c` was added to object type `Query`" in stdout.out
    assert "⚠️ Default value for argument `x` on field `Field.calculus` changed from `0` to `100`" in stdout.out


def test_schema_default_mode_json_output(capsys):
    SCHEMA_FILE = 'tests/data/simple_schema.gql'
    ANOTHER_SCHEMA_FILE = 'tests/data/simple_schema_dangerous_changes.gql'
    args = parse_args([
        '--old-schema', SCHEMA_FILE,
        '--new-schema', ANOTHER_SCHEMA_FILE,
        '--as-json'
    ])
    exit_code = main(args)
    assert exit_code == 0

    stdout = capsys.readouterr().out
    result = json.loads(stdout)
    assert result == {
        '1e3b776bda2dd8b11804e7341bb8b2d1': {
            'criticality': {
                'level': 'NON_BREAKING',
                'reason': "This change won't break any preexisting query"
            },
            'is_safe_change': True,
            'message': 'Field `c` was added to object type `Query`',
            'path': 'Query.c'
        },
        'a43d73d21c69cbd72334c06904439f50': {
            'criticality': {
                'level': 'DANGEROUS',
                'reason': 'Changing the default value for an argument '
                          'may change the runtime behaviour of a field if it was never provided.'
            },
            'is_safe_change': False,
            'message': 'Default value for argument `x` on field `Field.calculus` changed from `0` to `100`',
            'path': 'Field.calculus'
        }
    }


def test_schema_strict_mode(capsys):
    SCHEMA_FILE = 'tests/data/simple_schema.gql'
    ANOTHER_SCHEMA_FILE = 'tests/data/simple_schema_dangerous_changes.gql'
    args = parse_args([
        '-o', SCHEMA_FILE,
        '--new-schema', ANOTHER_SCHEMA_FILE,
        '--strict'
    ])
    exit_code = main(args)
    #  As we run the comparison in strict mode and there is a dangerous change, the exit code is 1
    assert exit_code == 1

    stdout = capsys.readouterr()
    assert "✔️ Field `c` was added to object type `Query`" in stdout.out
    assert "⚠️ Default value for argument `x` on field `Field.calculus` changed from `0` to `100`" in stdout.out


def test_schema_tolerant_mode(capsys):
    SCHEMA_FILE = 'tests/data/simple_schema.gql'
    ANOTHER_SCHEMA_FILE = 'tests/data/simple_schema_dangerous_changes.gql'
    args = parse_args([
        '-o', SCHEMA_FILE,
        '--new-schema', ANOTHER_SCHEMA_FILE,
        '--tolerant'
    ])
    exit_code = main(args)
    #  In tolerant mode, dangerous changes don't cause an error exit code
    assert exit_code == 0

    stdout = capsys.readouterr()
    assert "✔️ Field `c` was added to object type `Query`" in stdout.out
    assert "⚠️ Default value for argument `x` on field `Field.calculus` changed from `0` to `100`" in stdout.out
    assert len(stdout.out.split('\n')) == 3


def test_schema_strict_mode_with_breaking_changes_gives_error_exit_code(capsys):
    SCHEMA_FILE = 'tests/data/simple_schema.gql'
    ANOTHER_SCHEMA_FILE = 'tests/data/simple_schema_breaking_changes.gql'
    args = parse_args([
        '-o', SCHEMA_FILE,
        '--new-schema', ANOTHER_SCHEMA_FILE,
        '--strict'
    ])
    exit_code = main(args)
    assert exit_code == 1

    stdout = capsys.readouterr()
    assert '❌ Field `a` was removed from object type `Query`\n' in stdout.out
    assert len(stdout.out.split('\n')) == 2


def test_cli_exits_normally_by_default_when_strict_or_tolerant_mode_is_specified(capsys):
    SCHEMA_FILE = 'tests/data/simple_schema.gql'
    BREAKING_CHANGES_SCHEMA = 'tests/data/simple_schema_breaking_changes.gql'
    args = parse_args([
        '--old-schema', SCHEMA_FILE,
        '-n', BREAKING_CHANGES_SCHEMA,
    ])
    exit_code = main(args)
    assert exit_code == 0

    stdout = capsys.readouterr()
    assert '❌ Field `a` was removed from object type `Query`\n' in stdout.out
    assert len(stdout.out.split('\n')) == 2


def test_tolerant_mode_doesnt_allow_breaking_changes(capsys):
    SCHEMA_FILE = 'tests/data/simple_schema.gql'
    BREAKING_CHANGES_SCHEMA = 'tests/data/simple_schema_breaking_changes.gql'
    tolerant_args = parse_args([
        '-o', SCHEMA_FILE,
        '-n', BREAKING_CHANGES_SCHEMA,
        '--tolerant'
    ])
    default_args = parse_args([
        '-o', SCHEMA_FILE,
        '-n', BREAKING_CHANGES_SCHEMA,
    ])
    exit_code = main(tolerant_args)
    assert exit_code == 1

    exit_code = main(default_args)
    assert exit_code == 0


def test_cli_function(capsys):
    SCHEMA_FILE = 'tests/data/simple_schema.gql'
    command_args = [
        'schemadiff',
        '-o', SCHEMA_FILE,
        '-n', SCHEMA_FILE,
    ]
    with patch.object(sys, 'argv', command_args):
        exit_code = cli()
        assert exit_code == 0
        assert capsys.readouterr().out == '🎉 Both schemas are equal!\n'
