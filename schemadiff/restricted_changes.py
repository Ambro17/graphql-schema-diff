
def evaluate_if_restricted_change(change_type, change):
    # ToDo: Work better on this!
    from schemadiff.changes.type import AddedType
    if isinstance(change_type, AddedType):
        return not change.description

    from schemadiff.changes.type import TypeDescriptionChanged
    if isinstance(change_type, TypeDescriptionChanged):
        return not change
