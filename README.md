# fnversion
Small tool to support multiple versions of the same function or method in Python.

```python
    class SampleVersionManager(VersionManager):
        def get_version_number(instance=None, owner=None, args=None, kwargs=None):
            return args[0]

    @VersionManager(1)
    def versioned_method(version, num):
        return num * 1

    @versioned_method.version(2)
    def versioned_method(version, num):
        return num * 2

    @versioned_method.version(5)
    def versioned_method(version, num):
        return num * 3


    try:
        versioned_method(0, 12)
    except VersionError as exc:
        assert exc.args[0] == 'No suitable version found.'
    assert versioned_method(1, 12) == 12
    assert versioned_method(2, 12) == 24
    assert versioned_method(3, 12) == 24
    assert versioned_method(4, 12) == 24
    assert versioned_method(5, 12) == 36
    assert versioned_method(6, 12) == 36
    assert versioned_method(7, 12) == 36
```
