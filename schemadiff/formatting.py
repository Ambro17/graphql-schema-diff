from schemadiff import Change
from schemadiff.changes import CriticalityLevel


def format_diff(changes: [Change]) -> str:
    changes = '\n'.join(
        format_change_by_criticality(change)
        for change in changes
    )
    return changes or '🎉 Both schemas are equal!'


def format_change_by_criticality(change: Change) -> str:
    icon_by_criticality = {
        CriticalityLevel.Breaking: '❌',
        CriticalityLevel.Dangerous: '🚸',
        CriticalityLevel.NonBreaking: '✅',
    }
    icon = icon_by_criticality[change.criticality.level]
    return f"{icon} {change.message}"
