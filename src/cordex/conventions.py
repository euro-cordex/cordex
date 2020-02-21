# -*- coding: utf-8 -*-
# flake8: noqa
"""conventions module

This module defines file naming conventions in the :class:`FileConvention`.

"""

import os
import glob
import pandas as pd
import numpy as np
import logging
from parse import parse
import string
from pathlib import Path, PurePath
from cordex import __version__

__author__ = "Lars Buntemeyer"
__copyright__ = "Lars Buntemeyer"
__license__ = "mit"

_logger = logging.getLogger(__name__)


class NamingConvention():
    def __init__(self):
        pass


class Formatter(object):

    def __init__(self, name, fmt=None, parser=None):
        self.name   = name
        self.fmt    = fmt
        self.parser = parser
        if self.parser:
            self.parse_dict = {self.name:self.parser}
        else:
            self.parse_dict = None

    def parse(self, s):
        return parse('{:'+self.name+'}' , s, self.parse_dict).fixed

    def format(self, fill):
        return ('{:'+self.fmt+'}').format(fill)


class FileNameConvention(NamingConvention):
    """creates and parse filenames according to a convention.
    """

    def __init__(self, conv_str='', any_str='*', formatters=None):
        NamingConvention.__init__(self)
        self.conv_str    = conv_str
        self.any_str     = any_str
        # save the attribtes from the convention str
        #self.attr_names  = parse(self.conv_str, self.conv_str, self.parse_dict).named.keys()
        self.attr_names = [t[1] for t in string.Formatter().parse(conv_str) if t[1] is not None]
        self.defaults    = {attr:self.any_str for attr in self.attr_names}
        self.formatters  = formatters
        if formatters is None:
            self.formatters = {}

    def parse_attrs(self, attrs):
        return attrs

    def format_attrs(self, attrs, any_str):
        return attrs

    def parse(self, filename):
        """Parses a filename and returns attributes.
        """
        attrs = parse(self.conv_str, os.path.basename(filename)).named
        attrs = self.parse_attrs(attrs)
        return attrs


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
        attrs_dict = self.format_attrs(attrs_dict, any_str)
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
    """Holds a pandas DataFrame of file attributes.

    The pandas Dataframe holds a list of files
    that fullfill a convention and stores attributes
    derived from the filename and path.
    """

    def __init__(self, df):
        self.df = df

    def subset(self, **kwargs):
        """Create a subset by filtering attributes.
        """
        df = self.df[np.logical_and.reduce([(self.df[i] == j) for i, j in kwargs.items()])]
        return FileSelection(df)

    def __str__(self):
        text = ''
        text += str(self.df)
        return text

    def to_csv(self, filename):
        self.df.to_csv(filename)

    def attributes(self):
        for key in self.df:
            print('attribute {}, found {}'.format(key,self.df[key].unique()))

    @property
    def file_list(self):
        return list(self.df.index.values)

    def __getitem__(self, key):
        return self.df[key]

    def __iter__(self):
        return iter(self.df)


def make_df(convention, files):
    """Creates a Pandas DataFrame object from convention and files.

    This function creates a Pandas DataFrame object by parsing a list
    of files according to a convention of type :class:`FileConvention`.
    """
    df = pd.DataFrame()
    for f in files:
        _logger.debug('parsing file: {}'.format(f))
        if not os.path.isfile(f):
            _logger.warning('ignoring {}'.format(f))
            continue
        attrs = convention.parse(f)
        df = pd.concat([df, pd.DataFrame(attrs, index=[f])])
    return df


def select_files(convention, filter={}, root=None, ignore_path=False):
    """Creates a file list by searching the filesystem.

    The file list is created by using a search pattern according to a
    :class:`FileConvention`, :class:`FileNameConvention` or
    :class:`FilePathConvention`.

    Args:
        convention (:class:`FileConvention`): The convention used for
            browsing the file system.
        filter (dict): Defines attributes to filer the search.
        root (str): The root directory where the convention holds.

    Returns:
        List of full filenames.

    """
    if root:
        convention.root = root
    pattern = convention.pattern(**filter)
    logging.info('looking for files: {}'.format(pattern))
    return glob.glob(pattern)


def get_selection(convention, filter={}, root=None, ignore_path=False):
    """Top level function to create a :class:`FileSelection` instance.

    This function creates a :class:`FileSelection` instance
    using a file naming convention of type :class:``FileConvention`.

    Args:
        convention (:class:`FileConvention`): The convention used for
            browsing the file system.
        filter (dict): Defines attributes to filer the search.
        root (str): The root directory where the convention holds.

    Returns:
        :class:`FileSelection` object.

    """
    files = select_files(convention, filter, root, ignore_path)
    df    = make_df(convention, files)
    return FileSelection(df)

