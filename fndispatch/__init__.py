"""
Small tool to support multiple versions of the same function or method in Python.

Sample usage:

    class SampleVersionManager(VersionManager):
        def get_version_number(instance=None, owner=None, args=None, kwargs=None):
            return args[0]

    @VersionManager(1)
    def versioned_method(version, num):
        return num * 1

    @versioned_method.register_version(2)
    def versioned_method(version, num):
        return num * 2

    @versioned_method.register_version(5)
    def versioned_method(version, num):
        return num * 3


    try:
        versioned_method(0, 12)
    except VersionNotFound as exc:
        assert exc.args[0] == 'No suitable version found'
    assert versioned_method(1, 12) == 12
    assert versioned_method(2, 12) == 24
    assert versioned_method(3, 12) == 24
    assert versioned_method(4, 12) == 24
    assert versioned_method(5, 12) == 36
    assert versioned_method(6, 12) == 36
    assert versioned_method(7, 12) == 36
"""
__author__ = "Simon Sagi"
__license__ = "GNU GENERAL PUBLIC LICENSE"
__version__ = "1.0"

import inspect

from fndispatch.exceptions import VersionTooLow, VersionTooHigh, VersionNotFound


class VersionManager(object):
    """  This is the class for providing the correct version if exists.
    It collects all the functions with the corresponding decorator, order it and choose the right one when you try to
    load it.
    """
    def __init__(self, initial_version, min_version=None, max_version=None, fallback=True):
        self._versions = {}
        self._keys = []
        self._next_version = initial_version
        self._min_version = min_version
        self._max_version = max_version
        self._fallback = fallback
        self._function_name = None

    def __call__(self, *args, **kwargs):
        if self._next_version is not None:
            return self._set_new_version(*args, **kwargs)

        version_number = self.get_version_number(args=args, kwargs=kwargs)
        version_func = self._get_version(version_number)

        return version_func(*args, **kwargs)

    def _set_new_version(self, *args, **kwargs):
        if kwargs or len(args) != 1:
            raise TypeError('Version saver expects exactly 1 argument ({0} given)'.format(len(args) + len(kwargs)))

        func = args[0]
        if not inspect.isfunction(func) and not inspect.ismethod(func):
            raise TypeError('Version saver expects function or method')

        self._versions[self._next_version] = func
        self._next_version = None
        self._keys = list(self._versions.keys())
        self._keys.sort(reverse=True)

        # Save the name of the decorated function for later use
        if self._function_name is None:
            self._function_name = func.__name__
        return self

    def __get__(self, instance, owner):
        # If _next_version is set, we are setting up a new version and not getting an old one.
        if self._next_version is not None:
            return self

        def version_wrapper(*args, **kwargs):
            # Get the version number and the corresponding function
            version_number = self.get_version_number(instance=instance, owner=owner, args=args, kwargs=kwargs)
            version_func = self._get_version(version_number)

            # It's a classmethod
            if instance is None:
                return version_func(owner, *args, **kwargs)
            # It's a bounded method
            else:
                return version_func(instance, *args, **kwargs)

        version_wrapper.__name__ = self._function_name
        return version_wrapper

    def register_version(self, version):
        if self._next_version is not None:
            raise TypeError('Next version number already set. Cannot set it twice.')

        if self._next_version in self._versions:
            raise ValueError('This version is already registered.')

        self._next_version = version
        return self

    def _get_version(self, version_number):
        if not self._fallback:
            try:
                return self._versions[version_number]
            except KeyError:
                return self.no_version_found(version_number)

        if self._min_version is not None and version_number < self._min_version:
            return self.too_low_version(version_number)

        if self._max_version is not None and version_number > self._max_version:
            return self.too_high_version(version_number)

        for i in range(len(self._keys)):
            if self._keys[i] <= version_number:
                break
        else:
            return self.no_version_found(version_number)

        return self._versions[self._keys[i]]

    @staticmethod
    def get_version_number(instance=None, owner=None, args=None, kwargs=None):
        """
        Get the version number here. Have to be overridden in the subclass to support different version number sources.
        Usage of the function:
          Versioned functions are methods:
            Instance is the instance of class where the method is bounded to. Owner is the class of the instance.
            Args and kwargs are None.
          Versioned functions are classmethods:
            Instance is None. Class is the class which have the version manager.
            Args and kwargs are None.
          Versioned functions are standard functions or staticmethods:
            Instance and class is None.
            Args and kwargs are the arguments and keyword arguments sent to the function.
        Should return the version number as an integer.
        :type args: tuple
        :type kwargs: dict
        :rtype: int
        """
        raise NotImplementedError

    @staticmethod
    def too_low_version(version_number):
        raise VersionTooLow('Version number is too low')

    @staticmethod
    def too_high_version(version_number):
        raise VersionTooHigh('Version number is too high')

    @staticmethod
    def no_version_found(version_number):
        raise VersionNotFound('No suitable version found')
