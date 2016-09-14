
from fnversion import VersionManager
from fnversion.exceptions import VersionError


class DjangoMethodVersionManager(VersionManager):
    def _get_version(self, version_number):
        # If the registered method has no suitable version, rather return 405 than 404 to the client
        try:
            return super(DjangoMethodVersionManager, self)._get_version(version_number)
        except VersionError:
            # Django dispatch function handles AttributeError as `405 - Method not allowed` (using `getattr()`)
            raise AttributeError