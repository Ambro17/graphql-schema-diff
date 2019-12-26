from schemadiff.changes import Change, Criticality


def test_safe_change():
    class NonBreakingChange(Change):
        criticality = Criticality.safe('this is a safe change')

        def message(self):
            return 'test message'

        def path(self):
            return 'test path'

    c = NonBreakingChange()
    assert c.breaking is False
    assert c.dangerous is False
    assert c.safe is True
    assert c.criticality.reason == 'this is a safe change'


def test_breaking_change():
    class BreakingChange(Change):
        criticality = Criticality.breaking('this is breaking')

        def message(self):
            return 'test message'

        def path(self):
            return 'test path'

    c = BreakingChange()
    assert c.breaking is True
    assert c.dangerous is False
    assert c.safe is False
    assert c.criticality.reason == 'this is breaking'


def test_dangerous_change():
    class DangerousChange(Change):
        criticality = Criticality.dangerous('this is dangerous')

        def message(self):
            return 'test message'

        def path(self):
            return 'test path'

    c = DangerousChange()
    assert c.breaking is False
    assert c.dangerous is True
    assert c.safe is False
    assert c.criticality.reason == 'this is dangerous'


def test_change_str_method_shows_change_message():
    class Testchange(Change):
        criticality = Criticality.safe('this is a safe change')

        @property
        def message(self):
            return 'test message'

        def path(self):
            return 'Query.path'

    change = Testchange()
    assert str(change) == 'test message'


def test_change_repr_simulates_class_instantiation():
    class Testchange(Change):
        criticality = Criticality.safe('this is a safe change')

        @property
        def message(self):
            return 'test message'

        @property
        def path(self):
            return 'Query.path'

    change = Testchange()
    print(repr(change))
    assert repr(change) == (
        "Change("
        "criticality=Criticality(level=CriticalityLevel.NonBreaking, reason=this is a safe change), "
        "message='test message', "
        "path='Query.path')"
    )
