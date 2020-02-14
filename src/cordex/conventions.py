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
from parse import parse
from pathlib import Path, PurePath
from cordex import __version__

__author__ = "Lars Buntemeyer"
__copyright__ = "Lars Buntemeyer"
__license__ = "mit"

_logger = logging.getLogger(__name__)


class NamingConvention():
    def __init__(self):
        pass


class FileNameConvention(NamingConvention):
    """creates and parse filenames according to a convention.
    """

    def __init__(self, conv_str='', any_str='*'):
        NamingConvention.__init__(self)
        self.conv_str    = conv_str
        self.any_str     = any_str
        # save the attribtes from the convention str
        self.attr_names  = parse(self.conv_str, self.conv_str).named.keys()
        self.defaults    = {attr:self.any_str for attr in self.attr_names}

    def parse(self, filename):
        """Parses a filename and returns attributes.
        """
        return parse(self.conv_str, os.path.basename(filename)).named

    def pattern(self, any_str=None, **kwargs):
        """Creates a filename pattern from attributes.
        """
        if any_str is None:
            any_str = self.any_str
            defaults = self.defaults
        else:
            defaults = {attr:any_str for attr in self.attr_names}
        attrs_dict = defaults.copy()
        attrs_dict.update(kwargs)
        return self.conv_str.format(**attrs_dict)


class FilePathConvention(NamingConvention):
    """creates and parse pathes according to a convention.
    """

    def __init__(self, conv_list=[], root=None, any_str='*'):
        NamingConvention.__init__(self)
        if root is None:
            self.root = ''
        else:
            self.root = root
        self.any_str   = any_str
        self.conv_list = conv_list

    def _build_str(self, keys, any_str=None, **kwargs):
        """creates a list of strings from attributes
        and keyword arguments according to a convention list.
        """
        build_str = []
        if any_str is None:
            any_str = self.any_str
        for key in keys:
            if key in kwargs:
                fill = kwargs[key]
            else:
                fill = any_str
            build_str.append(fill)
        return build_str

    @property
    def conv_str(self):
        """Returns a string describing the path convention.
        """
        return os.path.join(*self.conv_list)

    def parse(self, path):
        """Parses a path and returns attributes.
        """
        if self.root:
            path = str(PurePath(path).relative_to(self.root))
        values = path.split(os.sep)
        if len(values) != len(self.conv_list):
            print('path convention is: {}'.format(self.conv_str))
            raise Exception('path does not conform to convention: {}'.format(path))
        else:
            return dict(zip(self.conv_list,path.split(os.sep)))

    def pattern(self, root=None, **kwargs):
        """Creates a path pattern from attributes.
        """
        if root is None:
            root = self.root
        build_str = self._build_str(self.conv_list, **kwargs)
        return os.path.join(root, *build_str)


class FileConvention(object):
    """Combines a path and filename convention.

    This class combines the :class:`FilePathConvention` and
    :class:`FileNameConvention` into a fill filename with path
    convention.
    """

    def __init__(self, path_conv=None, filename_conv=None):
        self.path_conv     = path_conv
        self.filename_conv = filename_conv

    @property
    def root(self):
        """Sets the root of the path convention.
        """
        return self.path_conv.root

    @root.setter
    def root(self, root):
        """Returns the root of the path convention.
        """
        self.path_conv.root = root

    def parse(self, file):
        """Parses a file including path and filename and returns attributes.
        """
        path_attrs     = self.path_conv.parse(os.path.dirname(file))
        filename_attrs = self.filename_conv.parse(os.path.basename(file))
        path_attrs.update(filename_attrs)
        return path_attrs

    def filename(self, **kwargs):
        """Create a filename pattern.
        """
        return self.filename_conv.pattern(**kwargs)

    def path(self, root=None, **kwargs):
        """Creates path pattern.
        """
        if root is None:
            root = self.root
        return self.path_conv.pattern(root, **kwargs)

    def pattern(self, root=None, **kwargs):
        """Creates path and filename pattern.
        """
        if root is None:
            root = self.root
        return os.path.join(self.path(root=root,**kwargs),self.filename(**kwargs))



class FileSelection(object):
    """Creates a pandas DataFrame of file attributes.

    The pandas Dataframe holds a list of files
    that fullfill a convention and stores attributes
    derived from the filename and path.
    """

    def __init__(self, convention, files, ignore_path=False):
        self.convention = convention
        self.files  = files
        self.fdict   = {}
        self.pdict   = {}
        self.df  = pd.DataFrame()
        self._parse()

    def __str__(self):
        text = ''
        text += str(self.df)
        text += str(self.df.describe())
        return text

    def attributes(self):
        for key in self.df:
            print('attribute {}, found {}'.format(key,self.df[key].unique()))

    def __getitem__(self, key):
        return self.df[key]

    def __iter__(self):
        return iter(self.df)

    def _parse(self):
        for f in self.files:
            _logger.debug('parsing file: {}'.format(f))
            if not os.path.isfile(f):
                _logger.warning('ignoring {}'.format(f))
                continue
            attrs = self.convention.parse(f)
            df = pd.DataFrame(attrs, index=[f])
            self.df = pd.concat([self.df, df])



def select_files(convention, filter={}, root=None, ignore_path=False):
    """Top level function to create a :class:`FileSection` instance.

    This function creates a :class:`FileSelection` instance
    using a file naming convention of type :class:``FileConvention`.
    """
    if root:
        convention.root = root
    pattern = convention.pattern(**filter)
    _logger.info('looking for files: {}'.format(pattern))
    files = glob.glob(pattern)
    return FileSelection(convention, files, ignore_path)

