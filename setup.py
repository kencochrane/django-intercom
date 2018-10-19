# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

import os
import codecs
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname), 'rb', 'utf-8').read()


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}

README = read('README.rst')
PACKAGE = "django_intercom"
VERSION = "0.1.2"


setup(
    name='django-intercom',
    version=VERSION,
    description='Django App for integrating with intercom.io',
    maintainer='Ken Cochrane',
    maintainer_email='KenCochrane@gmail.com',
    url='https://github.com/kencochrane/django-intercom/',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    package_data=get_package_data('django_intercom'),
    packages=get_packages('django_intercom'),
    long_description=README,
    setup_requires=[
        'versiontools >= 1.8.2',
    ],
)
