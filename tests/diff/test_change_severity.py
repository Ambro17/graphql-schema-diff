from schemadiff.changes import Change, ApiChange


def test_safe_change():
    class NonBreakingChange(Change):
        criticality = ApiChange.safe('this is a safe change')

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
        criticality = ApiChange.breaking('this is breaking')

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
        criticality = ApiChange.dangerous('this is dangerous')

        def message(self):
            return 'test message'

        def path(self):
            return 'test path'

    c = DangerousChange()
    assert c.breaking is False
    assert c.dangerous is True
    assert c.safe is False
    assert c.criticality.reason == 'this is dangerous'
