import hashlib
import json
import os

from schemadiff.changes import CriticalityLevel, Change


def format_diff(changes: [Change]) -> str:
    changes = '\n'.join(
        format_change_by_criticality(change)
        for change in changes
    )
    return changes or '🎉 Both schemas are equal!'


def format_change_by_criticality(change: Change) -> str:
    icon_by_criticality = {
        CriticalityLevel.Breaking: os.getenv('SD_BREAKING_CHANGE_ICON', '❌'),
        CriticalityLevel.Dangerous: os.getenv('SD_DANGEROUS_CHANGE_ICON', '⚠️'),
        CriticalityLevel.NonBreaking: os.getenv('SD_SAFE_CHANGE_ICON', '✔️'),
    }
    icon = icon_by_criticality[change.criticality.level]
    return f"{icon} {change.message}"


def print_diff(changes: [Change]) -> None:
    print(format_diff(changes))


def _change_key(message):
    return hashlib.md5(message.encode('utf-8')).hexdigest()


def changes_to_dict(changes: [Change]) -> [dict]:
    return [
        change.to_dict()
        for change in changes
    ]


def json_dump_changes(changes: [Change]) -> str:
    changes_ = changes_to_dict(changes)
    return json.dumps(
        {
            _change_key(change['message']): change
            for change in changes_
        }
    )


def print_json(changes) -> None:
    print(json_dump_changes(changes))
