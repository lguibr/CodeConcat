# -*- coding: utf-8 -*-
# codeconcat/__init__.py
import sys

__version__ = "0.0.0-unknown"  # Default

if sys.version_info >= (3, 8):
    # Use importlib.metadata for Python 3.8+
    from importlib.metadata import PackageNotFoundError, version

    try:
        __version__ = version("codeconcat")
    except PackageNotFoundError:
        # Package is not installed, perhaps running from source
        __version__ = "0.0.0-dev (importlib)"
else:
    # Use pkg_resources for Python < 3.8
    try:
        import pkg_resources

        try:
            __version__ = pkg_resources.get_distribution("codeconcat").version
        except pkg_resources.DistributionNotFound:
            __version__ = "0.0.0-dev (pkg_resources)"
    except ImportError:
        # pkg_resources might not be installed either in very minimal environments
        __version__ = "0.0.0-dev (pkg_resources import failed)"


# You can also import key functions here if you want them accessible like:
# from .main import main
