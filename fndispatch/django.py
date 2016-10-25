
from fndispatch import VersionManager
from fndispatch.exceptions import VersionNotFound


class DjangoMethodVersionManager(VersionManager):
    def _get_version(self, version_number):
        # If the registered method has no suitable version, rather return 405 than 404 to the client
        try:
            return super(DjangoMethodVersionManager, self)._get_version(version_number)
        except VersionNotFound:
            # Django dispatch function handles AttributeError as `405 - Method not allowed` (using `getattr()`)
            raise AttributeError

    @staticmethod
    def get_version_number(instance=None, owner=None, args=None, kwargs=None):
        # Django view first argument is always the request
        # To make this work either use Django REST Framework or set the `version` attribute before accessing it
        return args[0].version