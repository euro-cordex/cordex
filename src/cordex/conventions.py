# -*- coding: utf-8 -*-
# flake8: noqa
"""conventions module

This module defines file naming conventions in the
:class:``FileConvention`.

"""

import os
import logging
from cordex import __version__

__author__ = "Lars Buntemeyer"
__copyright__ = "Lars Buntemeyer"
__license__ = "mit"

_logger = logging.getLogger(__name__)


class NamingConvention():
    def __init__(self):
        pass


class FilePathConvention(NamingConvention):
    def __init__(self):
        NamingConvention.__init__(self)


class FileNameConvention(NamingConvention):
    def __init__(self):
        NamingConvention.__init__(self)


class FileConvention(object):
    """This class defines a file naming convention.

    This class defines conventions for a path and filename and
    adds functions to build a path and filename.

    """

    def __init__(self, root='', defaults={}):
        self.root      = root
        self.defaults  = defaults
        self.name      = ''
        self.suffix    = ''
        self.path_conv = []
        self.file_conv = []
        self.separator = '_'

    @staticmethod
    def name():
       return self.name

    def _build_str(self, keys, anystr='*', **kwargs):
        """creates a list of strings from default attributes
        or keyword arguments according to a convention list.
        """
        build_str = []
        for key in keys:
            if key in kwargs:
                fill = kwargs[key]
            elif key in self.defaults:
                fill = self.defaults[key]
            else:
                fill = anystr
            build_str.append(fill)
        return build_str


    def path(self, **kwargs):
        """Build a path.
        """
        build_str = self._build_str(self.path_conv, **kwargs)
        return os.path.join(self.root, *build_str)

    def file(self, **kwargs):
        """Build a filename.
        """
        build_str = self._build_str(self.file_conv, **kwargs)
        return self.separator.join(build_str) + self.suffix

    def filename(self, **kwargs):
        """Build a full path including filename.
        """
        return os.path.join(self.path(**kwargs), self.file(**kwargs))


