from graphql import build_schema as schema

from diff.compare import SchemaComparator


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
    diff = SchemaComparator(a, b).compare()
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

    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "Field 'favorite_number' of type 'Float' was added to interface 'Person'"

    diff = SchemaComparator(b, a).compare()
    assert diff[0].message() == "Field 'favorite_number' was removed from interface 'Person'"


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
    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "Field 'Person.age' type changed from 'Int' to 'Float!'"


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
    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "'Person.age' description changed from 'desc' to 'other desc'"


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
    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 1
    assert diff[0].message() == "'Person.age' deprecation reason changed from 'No longer supported' to 'my reason'"


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
    diff = SchemaComparator(a, b).compare()
    assert diff and len(diff) == 3
    expected_diff = {
        "Field 'b' was added to object type 'MyType'",
        "Type 'InterfaceB' was added",
        "'MyType' implements new interface 'InterfaceB'"
    }
    for change in diff:
        assert change.message() in expected_diff

    diff = SchemaComparator(b, a).compare()
    assert diff and len(diff) == 3
    expected_diff = {
        "Field 'b' was removed from object type 'MyType'",
        "Type 'InterfaceB' was removed",
        "'MyType' no longer implements interface 'InterfaceB'"
    }
    for change in diff:
        assert change.message() in expected_diff
