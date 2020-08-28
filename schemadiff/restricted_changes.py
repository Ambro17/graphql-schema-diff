from typing import List

from schemadiff.restrictions import Restriction


def evaluate_restrictions(diff, restrictions: List[str]) -> bool:
    """Given a diff between schemas and a list of restriction
    names, it looks up for all restrictions matching the list
    and evaluates the changes against that list.

    Returns:
        bool: True if there is at least one restricted change,
            False otherwise.
    """
    is_restricted = False
    restrictions = Restriction.get_subclasses_by_names(restrictions)
    for change in diff:
        if any(restriction.is_restricted(change) for restriction in restrictions):
            change.protected = True
            is_restricted = True

    return is_restricted


def restrictions_list():
    return Restriction.get_restrictions_list()

