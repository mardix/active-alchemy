# -*- coding: utf-8 -*-
b'This library requires Python 2.6, 2.7, 3.3, 3.4 or pypy'
import io
import os
import re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


PACKAGE = 'active_sqlalchemy'


def get_path(*args):
    return os.path.join(os.path.dirname(__file__), *args)


def read_from(filepath):
    with io.open(filepath, 'rt', encoding='utf8') as f:
        return f.read()


def get_version():
    data = read_from(get_path(PACKAGE, '__init__.py'))
    version = re.search(r"__version__\s*=\s*u?'([^']+)'", data).group(1)
    return str(version)


def find_package_data(root, include_files=('.gitignore', )):
    files = []
    src_root = get_path(root).rstrip('/') + '/'
    for dirpath, subdirs, filenames in os.walk(src_root):
        path, dirname = os.path.split(dirpath)
        if dirname.startswith(('.', '_')):
            continue
        dirpath = dirpath.replace(src_root, '')
        for filename in filenames:
            is_valid_filename = not (
                filename.startswith('.') or
                filename.endswith('.pyc')
            )
            include_it_anyway = filename in include_files

            if is_valid_filename or include_it_anyway:
                files.append(os.path.join(dirpath, filename))
    return files


def find_packages_data(*roots):
    return dict([(root, find_package_data(root)) for root in roots])


def get_description():
    data = read_from(get_path(PACKAGE, '__init__.py'))
    desc = re.search('"""(.+)"""', data, re.DOTALL).group(1)
    return desc.strip()

setup(
    name='Active-SQLAlchemy',
    version=get_version(),
    author='Mardix',
    packages=[PACKAGE],
    package_data=find_packages_data(PACKAGE, 'tests'),
    zip_safe=False,
    url='http://github.com/mardix/active-sqlalchemy',
    download_url='http://github.com/mardix/active-sqlalchemy/tarball/master',
    license='MIT license (http://www.opensource.org/licenses/mit-license.php)',
    description='A framework agnostic wrapper for SQLAlchemy that makes it really easy to use by implementing some activerecord like api',
    long_description=get_description(),
    install_requires=[
        "inflection>=0.2.0",
        "SQLAlchemy>=0.8",
        "PyMySQL>=0.6.1"
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
    ]
)
