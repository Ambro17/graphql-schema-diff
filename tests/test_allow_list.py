import json

import pytest

from schemadiff.allow_list import read_allowed_changes, InvalidAllowlist


def test_read_from_invalid_json():
    with pytest.raises(InvalidAllowlist, match='Invalid json format provided.'):
        read_allowed_changes("")


def test_allow_list_is_not_a_mapping():
    with pytest.raises(InvalidAllowlist, match='Allowlist must be a mapping.'):
        read_allowed_changes("[]")


def test_allow_list_keys_are_not_change_checksums():
    with pytest.raises(InvalidAllowlist, match='All keys must be a valid md5 checksum'):
        read_allowed_changes(json.dumps(
            {
                '1e3b776bda2dd8b11804e7341bb8b2d1': 'md5 checksum key',
                'bad key': 'some message'
            }
        ))


def test_read_from_valid_json():
    original = """{
            "1e3b776bda2dd8b11804e7341bb8b2d1": "lorem",
            "1234776bda2dd8b11804e7341bb8b2d1": "ipsum"
    }"""
    assert read_allowed_changes(original) == json.loads(original) == {
        "1e3b776bda2dd8b11804e7341bb8b2d1": "lorem",
        "1234776bda2dd8b11804e7341bb8b2d1": "ipsum",
    }