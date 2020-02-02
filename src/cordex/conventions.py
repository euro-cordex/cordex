# -*- coding: utf-8 -*-
# flake8: noqa
"""conventions module

This module defines file naming conventions in the
:class:``FileConvention`.

"""

import os
import glob
import pandas as pd
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
        self.file_sep  = '_'

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

        Adding a slash at the end here to avoid file results.
        """
        build_str = self._build_str(self.path_conv, **kwargs)
        return os.path.join(self.root, *build_str) #+ '/'

    def file(self, **kwargs):
        """Build a filename.
        """
        build_str = self._build_str(self.file_conv, **kwargs)
        return self.file_sep.join(build_str) + self.suffix

    def filename(self, **kwargs):
        """Build a full path including filename.
        """
        return os.path.join(self.path(**kwargs), self.file(**kwargs))


class StringAttributes(object):
    """Derives attributes from a string using a separator.

    This class derives attributes from a string by
    splitting it using a separator and storing them as
    attributes using a list of attributes to look for.
    """
    def __init__(self, str, attrs, sep):
        self.sep   = sep
        self.attrs = attrs
        values = str.split(self.sep)[-len(attrs):]
        self._init_attributes(attrs, values)

    def _init_attributes(self, attrs, values):
        """Creates attributes and values
        """
        for attr, value in zip(attrs, values):
            self.__setattr__(attr, value)

    def attributes(self):
        return {key:getattr(self,key) for key in self.attrs}


class PathAttributes(StringAttributes):
    """Derives attributes from a system path.

    This class derives attributes from a filename by
    splitting it using a separator.
    """
    def __init__(self, path, attrs):
        StringAttributes.__init__(self, path, attrs, os.sep)


class FileAttributes(StringAttributes):
    """Derives attributes from a filename.

    This class derives attributes from a filename by
    splitting it using a separator.
    """
    def __init__(self, file, attrs, sep):
        StringAttributes.__init__(self, file, attrs, sep)


class FileSelection(object):
    """Holds a list of files :class:`PathAttributes` instances.
    """

    def __init__(self, convention, pathes=[]):
        self.convention = convention
        self.pathes = pathes
        self.datapathes = []
        self.files = []
        self.fdict   = {}
        self.pdict   = {}
        self.df  = pd.DataFrame()
        self._init_files()

    def __getitem__(self, key):
        return self.df[key]

    def __iter__(self):
        return iter(self.df)

    def _init_files(self):
        for path in self.pathes:
            pattrs = PathAttributes(path, self.convention.path_conv)
            self.datapathes.append(pattrs)
            self.pdict[path] = pattrs.attributes()
            files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            for f in files:
                fattrs = FileAttributes(f, self.convention.file_conv, self.convention.file_sep)
                self.files.append(fattrs)
                self.fdict[f] = fattrs.attributes()
                self.fdict[f].update(self.pdict[path])
                df = pd.DataFrame(self.fdict[f], index=[os.path.join(path,f)])
                self.df = pd.concat([self.df, df])


def select_files(convention, root='', filter={}):
    """Top levels function to select files.

    This function creates a :class:`FileSelection` instance
    using a file naming convention of type :class:``FileConvention`.
    """
    convention.root = root
    convention.defaults = filter
    pattern = convention.path()
    _logger.info('looking for files in: {}'.format(pattern))
    pathes = glob.glob(pattern)
    return FileSelection(convention, pathes)

