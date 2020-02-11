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
from pathlib import Path
from cordex import __version__

__author__ = "Lars Buntemeyer"
__copyright__ = "Lars Buntemeyer"
__license__ = "mit"

_logger = logging.getLogger(__name__)


class NamingConvention():
    def __init__(self):
        pass


class FileNameConvention(NamingConvention):

    def __init__(self, conv_str='', any_str='*'):
        NamingConvention.__init__(self)
        self.conv_str    = conv_str
        self.any_str     = any_str
        # save the attribtes from the convention str
        self.attr_names  = parse(self.conv_str, self.conv_str).named.keys()
        self.defaults    = {attr:self.any_str for attr in self.attr_names}

    def parse(self, filename):
        return parse(self.conv_str, Path(filename).name).named

    def filename(self, any_str=None, **kwargs):
        if any_str is None:
            any_str = self.any_str
            defaults = self.defaults
        else:
            defaults = {attr:any_str for attr in self.attr_names}
        attrs_dict = defaults.copy()
        attrs_dict.update(kwargs)
        return self.conv_str.format(**attrs_dict)


class FilePathConvention(NamingConvention):

    def __init__(self, conv_list=[], root='', any_str='*'):
        NamingConvention.__init__(self)
        self.root      = root
        self.any_str   = any_str
        self.conv_list = conv_list

    def _build_str(self, keys, any_str=None, **kwargs):
        """creates a list of strings from default attributes
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
    def path_conv(self):
        return os.path.join(*self.conv_list)

    def parse(self, path):
        values = path.split(os.sep)
        if len(values) != len(self.conv_list):
            print('path convention is: {}'.format(self.path_conv))
            raise Exception('path does not conform to convention: {}'.format(path))
        else:
            return dict(zip(self.conv_list,path.split(os.sep)))

    def path(self, **kwargs):
        """Build a path.

        Adding a slash at the end here to avoid file results.
        """
        build_str = self._build_str(self.conv_list, **kwargs)
        return os.path.join(self.root, *build_str)



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
        self.date_sep  = '-'
        self.conv_str  = ''

    @staticmethod
    def name():
       return self.name

    def _build_str(self, keys, anystr='*', **kwargs):
        """creates a list of strings from default attributes
        and keyword arguments according to a convention list.
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

    def parse(self, filename):
        return parse(self.conv_str, Path(filename).name).named

    def filename(self, attrs):
        return self.conv_str.format(**attrs)

    def path(self, **kwargs):
        """Build a path.

        Adding a slash at the end here to avoid file results.
        """
        build_str = self._build_str(self.path_conv, **kwargs)
        return os.path.join(self.root, *build_str)

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
        file_stem   = Path(file).stem
        self.suffix = Path(file).suffix
        StringAttributes.__init__(self, file_stem, attrs, sep)
        self.startdate = self.timerange.split('-')[0]
        self.enddate   = self.timerange.split('-')[1]
        self.attrs += (['startdate', 'enddate'])
        #print(self.attrs)

    def attributes(self):
        return {key:getattr(self,key) for key in self.attrs}


class FileSelection(object):
    """Creates a pandas DataFrame object.

    The pandas Dataframe holds a list of files
    that fullfill a convention and stores attributes
    derived from the filename and path.
    """

    def __init__(self, convention, pathes=[], ignore_path=False):
        self.convention = convention
        self.pathes = pathes
        self.ignore_path = ignore_path
        self.datapathes = []
        self.files = []
        self.fdict   = {}
        self.pdict   = {}
        self.df  = pd.DataFrame()
        self._init_files()

    def __str__(self):
        text = ''
        text += str(self.df)
        text += str(self.df.describe())
        return text

    def attributes(self):
        for key in self.df:
            print('attribute {}, found {}'.format(key,self.df[key].unique()))
       # print(pd.DataFrame({key:self.df[key].unique() for key in self.df}))
#         print(pd.DataFrame({'variable':self.df['variable'].unique()}))


    def __getitem__(self, key):
        return self.df[key]

    def __iter__(self):
        return iter(self.df)

    def _init_files(self):
        for path in self.pathes:
            _logger.debug('selecting path: {}'.format(path))
            if not os.path.isdir(path):
                _logger.warning('ignoring {}'.format(path))
                continue
            if not self.ignore_path:
                pattrs = PathAttributes(path, self.convention.path_conv)
                self.datapathes.append(pattrs)
                self.pdict[path] = pattrs.attributes()
            else:
                self.pdict[path] = {}
            files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            for f in files:
                #fattrs = FileAttributes(f, self.convention.file_conv, self.convention.file_sep)
                fattrs = self.convention.parse(f)
                self.files.append(fattrs)
                self.fdict[f] = fattrs #.attributes()
                self.fdict[f].update(self.pdict[path])
                df = pd.DataFrame(self.fdict[f], index=[os.path.join(path,f)])
                self.df = pd.concat([self.df, df])


def select_files(convention, root='', filter={}, ignore_path=False):
    """Top level function to create a :class:`FileSection` instance.

    This function creates a :class:`FileSelection` instance
    using a file naming convention of type :class:``FileConvention`.
    """
    convention.root = root
    convention.defaults = filter
    pattern = convention.path()
    _logger.info('looking for files in: {}'.format(pattern))
    pathes = glob.glob(pattern)
    return FileSelection(convention, pathes, ignore_path)

