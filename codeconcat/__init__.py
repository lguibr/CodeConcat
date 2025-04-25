# -*- coding: utf-8 -*-
# codeconcat/__init__.py
try:
    from importlib.metadata import PackageNotFoundError, version

    try:
        __version__ = version("codeconcat")
    except PackageNotFoundError:
        # Package is not installed, perhaps running from source
        __version__ = "0.0.0-dev"
except ImportError:
    # Fallback for Python < 3.8
    import pkg_resources

    try:
        __version__ = pkg_resources.get_distribution("codeconcat").version
    except pkg_resources.DistributionNotFound:
        __version__ = "0.0.0-dev"

# You can also import key functions here if you want them accessible like:
# from .main import main
