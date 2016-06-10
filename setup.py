#!/usr/bin/env python3
import os
from setuptools import setup, find_packages
from blumate.const import __version__

PACKAGE_NAME = 'blumate'
HERE = os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_URL = ('https://github.com/bdfoster/blumate/archive/'
                '{}.zip'.format(__version__))

PACKAGES = find_packages(exclude=['tests', 'tests.*'])

REQUIRES = [
    'requests>=2,<3',
    'pyyaml>=3.11,<4',
    'pytz>=2016.4',
    'pip>=7.0.0',
    'jinja2>=2.8',
    'voluptuous==0.8.9'
]

setup(
    name=PACKAGE_NAME,
    version=__version__,
    license='MIT License',
    url='https://home-assistant.io/',
    download_url=DOWNLOAD_URL,
    author='Brian Foster',
    author_email='me@bdfoster.com',
    description='Open-source automation hub running on Python 3.',
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=REQUIRES,
    test_suite='tests',
    keywords=['automation'],
    entry_points={
        'console_scripts': [
            'blumate = blumate.__main__:main'
        ]
    },
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5'
    ],
)
