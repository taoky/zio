#!/usr/bin/env python3

from setuptools import setup

from zio import __version__

import subprocess
import traceback

try:
    long_description = subprocess.check_output(['pandoc', 'README.md', '--to=rst'], universal_newlines=True)
except Exception as e:
    print("Notice: Please install pandoc to convert README.md to rst format, for PyPI")
    print("Continuing...")

setup(
    name='zio-py3',
    version=__version__,

    # author='Wenlei Zhu',
    # author_email='i@ztrix.me',
    url='https://github.com/taoky/zio',

    license='LICENSE.txt',
    keywords="zio pwning io expect-like",
    description='Unified io lib for pwning development written in python.',
    long_description=long_description,

    py_modules=['zio'],

    # Refers to test/test.py
    test_suite='test.test',

    entry_points={
        'console_scripts': [
            'zio=zio:main'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: System',
        'Topic :: Terminals',
        'Topic :: Utilities',
    ],
    python_requires='>=3.5',
)
