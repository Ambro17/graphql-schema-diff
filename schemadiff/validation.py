from schemadiff import Change
from typing import List

from dataclasses import dataclass

from schemadiff.validation_rules import ValidationRule


@dataclass
class ValidationResult:
    ok: bool
    errors: List['ValidationError']


@dataclass
class ValidationError:
    message: str


def validate_diff(diff: List[Change], rules: List[str]) -> ValidationResult:
    """Given a diff between schemas and a list of rules
    names, it looks up for all rules matching the list
    and evaluates the changes against that list.

    Returns:
        bool: True if there is at least one restricted change,
            False otherwise.
    """
    is_valid = True
    errors = []
    rules = ValidationRule.get_subclasses_by_names(rules)
    for change in diff:
        for rule in rules:
            if not rule(change).is_valid():
                change.restricted = rule(change).message
                is_valid = False
                errors.append(ValidationError(change.restricted))

    return ValidationResult(is_valid, errors)


def rules_list():
    return ValidationRule.get_rules_list()


evaluate_rules = validate_diff  # For retro-compatibility
