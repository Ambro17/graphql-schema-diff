from graphql import build_schema as schema

from schemadiff.changes import Criticality
from schemadiff.diff.schema import Schema


def test_interface_no_changes():
    a = schema("""
    interface Person {
      name: String
      age: Int
    }
    """)
    b = schema("""
    interface Person {
      age: Int
      name: String
    }
    """)
    diff = Schema(a, b).diff()
    assert not diff


def test_interface_field_added_and_removed():
    a = schema("""
    interface Person {
      name: String
      age: Int
    }
    """)
    b = schema("""
    interface Person {
      name: String
      age: Int
      favorite_number: Float
    }
    """)

    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "Field `favorite_number` of type `Float` was added to interface `Person`"
    assert diff[0].path == 'Person.favorite_number'
    assert diff[0].criticality == Criticality.dangerous(
        'Adding an interface to an object type may break existing clients '
        'that were not programming defensively against a new possible type.'
    )

    diff = Schema(b, a).diff()
    assert diff[0].message == "Field `favorite_number` was removed from interface `Person`"
    assert diff[0].path == 'Person.favorite_number'
    assert diff[0].criticality == Criticality.dangerous(
        'Removing an interface field can break existing queries that use this in a fragment spread.'
    )


def test_interface_field_type_changed():
    a = schema("""
    interface Person {
      age: Int
    }
    """)
    b = schema("""
    interface Person {
      age: Float!
    }
    """)
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "`Person.age` type changed from `Int` to `Float!`"
    assert diff[0].path == 'Person.age'
    assert diff[0].criticality == Criticality.breaking(
        'Changing a field type will break queries that assume its type'
    )


def test_interface_field_description_changed():
    a = schema('''
    interface Person {
        """desc"""
        age: Int
    }
    ''')
    b = schema('''
    interface Person {
        """other desc"""
        age: Int
    }
    ''')
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == "`Person.age` description changed from `desc` to `other desc`"
    assert diff[0].path == 'Person.age'
    assert diff[0].criticality == Criticality.safe()


def test_interface_field_deprecation_reason_changed():
    a = schema('''
    interface Person {
        age: Int @deprecated
    }
    ''')  # A default deprecation reason is appended on deprecation
    b = schema('''
    interface Person {
        age: Int @deprecated(reason: "my reason")
    }
    ''')
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 1
    assert diff[0].message == (
        "Deprecation reason on field `Person.age` changed from `No longer supported` to `my reason`"
    )
    assert diff[0].path == 'Person.age'
    assert diff[0].criticality == Criticality.safe()


def test_type_implements_new_interface():
    a = schema("""
    interface InterfaceA {
        a: Int
    }
    type MyType implements InterfaceA {
        a: Int
    }    
    """)
    b = schema("""
    interface InterfaceA {
        a: Int
    }
    interface InterfaceB {
        b: String
    }
    type MyType implements InterfaceA & InterfaceB {
        a: Int
        b: String
    }    
    """)
    diff = Schema(a, b).diff()
    assert diff and len(diff) == 3
    expected_diff = {
        "Field `b` was added to object type `MyType`",
        "Type `InterfaceB` was added",
        "`MyType` implements new interface `InterfaceB`"
    }
    expected_paths = {'InterfaceB', 'MyType', 'MyType.b'}
    for change in diff:
        assert change.message in expected_diff
        assert change.path in expected_paths

    diff = Schema(b, a).diff()
    assert diff and len(diff) == 3
    expected_diff = {
        "Field `b` was removed from object type `MyType`",
        "Type `InterfaceB` was removed",
        "`MyType` no longer implements interface `InterfaceB`"
    }
    expected_paths = {'InterfaceB', 'MyType', 'MyType.b'}
    for change in diff:
        assert change.message in expected_diff
        assert change.path in expected_paths
