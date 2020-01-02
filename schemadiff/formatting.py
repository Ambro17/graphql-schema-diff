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
