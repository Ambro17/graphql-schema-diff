from schemadiff import Change
from typing import List, Dict, Any

from dataclasses import dataclass

from schemadiff.validation_rules import ValidationRule


@dataclass
class ValidationResult:
    ok: bool
    errors: List['ValidationError']


@dataclass
class ValidationError:
    rule: str
    reason: str
    change: Change


def validate_changes(diff: List[Change], rules: List[str], allowed_changes: Dict[str, Any] = None) -> ValidationResult:
    """Given a list of changes between schemas and a list of rules,
    it runs all rules against the changes, to detect invalid changes.
    It also admits an allowlist of accepted invalid changes to document exceptions to the rules

    Returns:
        bool: True if there is at least one restricted change,
            False otherwise.
    """
    allowed_changes = allowed_changes or {}
    is_valid = True
    errors = []
    rules = ValidationRule.get_subclasses_by_names(rules)
    for change in diff:
        for rule in rules:
            if not rule(change).is_valid():
                if change.checksum() in allowed_changes:
                    continue

                change.restricted = rule(change).message
                is_valid = False
                errors.append(ValidationError(rule.name, change.restricted, change))

    return ValidationResult(is_valid, errors)


def rules_list():
    return ValidationRule.get_rules_list()
