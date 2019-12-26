from graphql import build_schema as schema

from schemadiff.changes import Criticality
from schemadiff.diff.schema import Schema


def test_added_removed_directive():
    no_directive = schema("""
    type A {
        a: String
    }
    """)
    one_directive = schema("""
    directive @somedir on FIELD_DEFINITION
    type A {
        a: String
    }
    """)
    diff = Schema(no_directive, one_directive).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "Directive `@somedir` was added to use on `FIELD_DEFINITION`"
    assert diff[0].path == '@somedir'
    assert diff[0].criticality == Criticality.safe()

    diff = Schema(one_directive, no_directive).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "Directive `@somedir` was removed"
    assert diff[0].path == '@somedir'
    assert diff[0].criticality == Criticality.breaking('Removing a directive may break clients that depend on them.')

    two_locations = schema("""
    directive @somedir on FIELD_DEFINITION | QUERY
    type A {
        a: String
    }
    """)
    diff = Schema(no_directive, two_locations).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "Directive `@somedir` was added to use on `FIELD_DEFINITION | QUERY`"
    assert diff[0].path == '@somedir'
    assert diff[0].criticality == Criticality.safe()


def test_description_changed():
    old_desc = schema('''
    """directive desc"""
    directive @somedir on FIELD_DEFINITION

    directive @nodesc on FIELD_DEFINITION

    """to be removed"""
    directive @toberemoveddesc on FIELD_DEFINITION

    type A {
        a: String
    }
    ''')
    new_desc = schema('''
    """updated desc"""
    directive @somedir on FIELD_DEFINITION
    
    """added desc"""
    directive @nodesc on FIELD_DEFINITION

    directive @toberemoveddesc on FIELD_DEFINITION

    type A {
        a: String
    }
    ''')
    diff = Schema(old_desc, new_desc).diff()
    assert diff and len(diff) == 3
    expected_diff = {
        "Description for directive `@somedir` changed from `directive desc` to `updated desc`",
        "Description for directive `@nodesc` changed from `None` to `added desc`",
        "Description for directive `@toberemoveddesc` changed from `to be removed` to `None`",
    }
    expected_paths = {'@somedir', '@nodesc', '@toberemoveddesc'}
    for change in diff:
        assert change.message in expected_diff
        assert change.path in expected_paths
        assert change.criticality == Criticality.safe()


def test_directive_location_added_and_removed():
    one_location = schema("""
    directive @somedir on FIELD_DEFINITION
    type A {
        a: String
    }
    """)
    two_locations = schema("""
    directive @somedir on FIELD_DEFINITION | FIELD
    type A {
        a: String
    }
    """)
    diff = Schema(one_location, two_locations).diff()
    assert diff and len(diff) == 1
    expected_message = (
        "Directive locations of `@somedir` changed from `FIELD_DEFINITION` to `FIELD_DEFINITION | FIELD`"
    )
    assert diff[0].message == expected_message
    assert diff[0].path == '@somedir'
    assert diff[0].criticality == Criticality.safe()

    diff = Schema(two_locations, one_location).diff()
    assert diff and len(diff) == 1
    expected_message = (
        "Directive locations of `@somedir` changed from `FIELD_DEFINITION | FIELD` to `FIELD_DEFINITION`"
    )
    assert diff[0].message == expected_message
    assert diff[0].path == '@somedir'
    assert diff[0].criticality == Criticality.breaking(
        'Removing a directive location will break any instance of its usage. Be sure no one uses it before removing it'
    )


def test_directive_argument_changes():
    name_arg = schema("""
    directive @somedir(name: String) on FIELD_DEFINITION
    type A {
        a: String
    }
    """)
    id_arg = schema("""
    directive @somedir(id: ID) on FIELD_DEFINITION
    type A {
        a: String
    }
    """)
    diff = Schema(name_arg, id_arg).diff()
    assert diff and len(diff) == 2
    expected_message = (
        'Removed argument `name: String` from `@somedir` directive'
        "Added argument `id: ID` to `@somedir` directive"
    )
    for change in diff:
        assert change.message in expected_message
        assert change.path == '@somedir'
        assert change.criticality == Criticality.breaking(
            'Removing a directive argument will break existing usages of the argument'
        ) if 'Removed' in change.message else Criticality.safe()


def test_directive_description_changed():
    no_desc = schema("""
    directive @my_directive on FIELD
    type A {
        a: String
    }
    """)
    with_desc = schema('''
    """directive desc"""
    directive @my_directive on FIELD
    type A {
        a: String
    }
    ''')
    new_desc = schema('''
    """new description"""
    directive @my_directive on FIELD
    type A {
        a: String
    }
    ''')
    diff = Schema(no_desc, with_desc).diff()
    assert diff and len(diff) == 1
    expected_message = (
        'Description for directive `@my_directive` changed from `None` to `directive desc`'
    )
    assert diff[0].message == expected_message
    assert diff[0].path == '@my_directive'
    assert diff[0].criticality == Criticality.safe()

    diff = Schema(with_desc, new_desc).diff()
    assert diff and len(diff) == 1
    expected_message = (
        'Description for directive `@my_directive` changed from `directive desc` to `new description`'
    )
    assert diff[0].message == expected_message
    assert diff[0].path == '@my_directive'
    assert diff[0].criticality == Criticality.safe()

    diff = Schema(with_desc, no_desc).diff()
    assert diff and len(diff) == 1
    expected_message = (
        'Description for directive `@my_directive` changed from `directive desc` to `None`'
    )
    assert diff[0].message == expected_message
    assert diff[0].path == '@my_directive'
    assert diff[0].criticality == Criticality.safe()


def test_directive_default_value_changed():
    default_100 = schema("""
    directive @limit(number: Int=100) on FIELD_DEFINITION
    type A {
        a: String
    }
    """)
    default_0 = schema("""
    directive @limit(number: Int=0) on FIELD_DEFINITION
    type A {
        a: String
    }
    """)

    diff = Schema(default_100, default_0).diff()
    assert diff and len(diff) == 1
    expected_message = (
        'Default value for argument `number` on `@limit` directive changed from `100` to `0`'
    )
    assert diff[0].message == expected_message
    assert diff[0].path == '@limit'
    assert diff[0].criticality == Criticality.dangerous(
        'Changing the default value for an argument may change '
        'the runtime behaviour of a field if it was never provided.'
    )


def test_directive_argument_type_changed():
    int_arg = schema("""
    directive @limit(number: Int) on FIELD_DEFINITION
    type A {
        a: String
    }
    """)
    float_arg = schema("""
    directive @limit(number: Float) on FIELD_DEFINITION
    type A {
        a: String
    }
    """)

    diff = Schema(int_arg, float_arg).diff()
    assert diff and len(diff) == 1
    expected_message = (
        "Type for argument `number` on `@limit` directive changed from `Int` to `Float`"
    )
    assert diff[0].message == expected_message
    assert diff[0].path == '@limit'
    assert diff[0].criticality == Criticality.breaking('Changing the argument type is a breaking change')


def test_directive_argument_description_changed():
    no_desc = schema("""
    directive @limit(
        number: Int
    ) on FIELD_DEFINITION

    type A {
        a: String
    }
    """)
    a_desc = schema("""
    directive @limit(
        "number limit"
        number: Int
    ) on FIELD_DEFINITION

    type A {
        a: String
    }
    """)
    other_desc = schema("""
    directive @limit(
        "field limit"
        number: Int
    ) on FIELD_DEFINITION

    type A {
        a: String
    }
    """)

    diff = Schema(no_desc, a_desc).diff()
    assert diff and len(diff) == 1
    expected_message = (
        "Description for argument `number` on `@limit` directive changed from `None` to `number limit`"
    )
    assert diff[0].message == expected_message
    assert diff[0].path == '@limit'
    assert diff[0].criticality == Criticality.safe()

    diff = Schema(a_desc, other_desc).diff()
    assert diff and len(diff) == 1
    expected_message = (
        "Description for argument `number` on `@limit` directive changed from `number limit` to `field limit`"
    )
    assert diff[0].message == expected_message
    assert diff[0].path == '@limit'
    assert diff[0].criticality == Criticality.safe()

    diff = Schema(other_desc, no_desc).diff()
    assert diff and len(diff) == 1
    expected_message = (
        "Description for argument `number` on `@limit` directive changed from `field limit` to `None`"
    )
    assert diff[0].message == expected_message
    assert diff[0].path == '@limit'
    assert diff[0].criticality == Criticality.safe()
