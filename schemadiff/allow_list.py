import json
import re
from json import JSONDecodeError


class InvalidAllowlist(Exception):
    """Exception raised when the user provides an invalid json file of allowed changes"""


def read_allowed_changes(file_content):
    """Read a json file that defines a mapping of changes checksums to the reasons of why it is allowed.

    Compliant formats:
        {
            '0cc175b9c0f1b6a831c399e269772661': 'Removed field `MyField` because clients don't use it',
            '92eb5ffee6ae2fec3ad71c777531578f': 'Removed argument `Arg` because it became redundant',
        }
        But the value can be as detailed as the user wants (as long as the key remains the change checksum)
        {
            '0cc175b9c0f1b6a831c399e269772661': {
                'date': '2030-01-01 15:00:00,
                'reason': 'my reason',
                'message': 'Field `a` was removed from object type `Query`'
            },
            '92eb5ffee6ae2fec3ad71c777531578f': {
                'date': '2031-01-01 23:59:00,
                'reason': 'my new reason',
                'message': 'Field `b` was removed from object type `MyType`'
            },
        }
    """
    try:
        allowlist = json.loads(file_content)
    except JSONDecodeError as e:
        raise InvalidAllowlist("Invalid json format provided.") from e
    if not isinstance(allowlist, dict):
        raise InvalidAllowlist("Allowlist must be a mapping.")

    CHECKSUM_REGEX = re.compile(r'[a-fA-F0-9]{32}')
    if any(not CHECKSUM_REGEX.match(checksum) for checksum in allowlist.keys()):
        raise InvalidAllowlist("All keys must be a valid md5 checksum")

    return allowlist
