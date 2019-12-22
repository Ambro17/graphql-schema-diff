from graphql import build_schema as schema

from diff.compare import SchemaComparator


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
    diff = SchemaComparator(no_directive, one_directive).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "Directive `@somedir` was added to use on `FIELD_DEFINITION`"

    diff = SchemaComparator(one_directive, no_directive).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "Directive `@somedir` was removed"

    two_locations = schema("""
    directive @somedir on FIELD_DEFINITION | QUERY
    type A {
        a: String
    }
    """)
    diff = SchemaComparator(no_directive, two_locations).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "Directive `@somedir` was added to use on `FIELD_DEFINITION | QUERY`"


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
    diff = SchemaComparator(old_desc, new_desc).compare()
    assert diff and len(diff) == 3
    expected_diff = {
        "Description for directive `@somedir` changed from `directive desc` to `updated desc`",
        "Description for directive `@nodesc` changed from `None` to `added desc`",
        "Description for directive `@toberemoveddesc` changed from `to be removed` to `None`",
    }
    for change in diff:
        assert change.message() in expected_diff


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
    diff = SchemaComparator(one_location, two_locations).compare()
    assert diff and len(diff) == 1
    expected_message = (
        "Directive locations of `@somedir` changed from `FIELD_DEFINITION` to `FIELD_DEFINITION | FIELD`"
    )
    assert diff[0].message() == expected_message

    diff = SchemaComparator(two_locations, one_location).compare()
    assert diff and len(diff) == 1
    expected_message = (
        "Directive locations of `@somedir` changed from `FIELD_DEFINITION | FIELD` to `FIELD_DEFINITION`"
    )
    assert diff[0].message() == expected_message


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
    diff = SchemaComparator(name_arg, id_arg).compare()
    assert diff and len(diff) == 2
    expected_message = (
        'Removed argument `name: String` from `@somedir` directive'
        "Added argument `id: ID` to `@somedir` directive"
    )
    for change in diff:
        assert change.message() in expected_message


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
    diff = SchemaComparator(no_desc, with_desc).compare()
    assert diff and len(diff) == 1
    expected_message = (
        'Description for directive `@my_directive` changed from `None` to `directive desc`'
    )
    assert diff[0].message() == expected_message

    diff = SchemaComparator(with_desc, new_desc).compare()
    assert diff and len(diff) == 1
    expected_message = (
        'Description for directive `@my_directive` changed from `directive desc` to `new description`'
    )
    assert diff[0].message() == expected_message

    diff = SchemaComparator(with_desc, no_desc).compare()
    assert diff and len(diff) == 1
    expected_message = (
        'Description for directive `@my_directive` changed from `directive desc` to `None`'
    )
    assert diff[0].message() == expected_message


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

    diff = SchemaComparator(default_100, default_0).compare()
    assert diff and len(diff) == 1
    expected_message = (
        'Default value for argument `number` on `@limit` directive changed from `100` to `0`'
    )
    assert diff[0].message() == expected_message


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

    diff = SchemaComparator(int_arg, float_arg).compare()
    assert diff and len(diff) == 1
    expected_message = (
        "Type for argument `number` on `@limit` directive changed from `Int` to `Float`"
    )
    assert diff[0].message() == expected_message


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

    diff = SchemaComparator(no_desc, a_desc).compare()
    assert diff and len(diff) == 1
    expected_message = (
        "Description for argument `number` on `@limit` directive changed from `None` to `number limit`"
    )
    assert diff[0].message() == expected_message

    diff = SchemaComparator(a_desc, other_desc).compare()
    assert diff and len(diff) == 1
    expected_message = (
        "Description for argument `number` on `@limit` directive changed from `number limit` to `field limit`"
    )
    assert diff[0].message() == expected_message

    diff = SchemaComparator(other_desc, no_desc).compare()
    assert diff and len(diff) == 1
    expected_message = (
        "Description for argument `number` on `@limit` directive changed from `field limit` to `None`"
    )
    assert diff[0].message() == expected_message
