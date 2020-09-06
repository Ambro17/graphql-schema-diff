from typing import List

from schemadiff.validation_rules import ValidationRule


def validate_diff(diff, rules: List[str]) -> bool:
    """Given a diff between schemas and a list of rules
    names, it looks up for all rules matching the list
    and evaluates the changes against that list.

    Returns:
        bool: True if there is at least one restricted change,
            False otherwise.
    """
    is_restricted = False
    rules = ValidationRule.get_subclasses_by_names(rules)
    for change in diff:
        for rule in rules:
            if not rule(change).is_valid():
                change.restricted = rule(change).message
                is_restricted = True

    return is_restricted


def rules_list():
    return ValidationRule.get_rules_list()


evaluate_rules = validate_diff  # For retro-compatibility
