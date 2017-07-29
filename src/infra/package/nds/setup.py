#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Babel==1.3',
    # 'git+ssh://git@bitbucket.org/rtxanson/babel_yaml.git@b28ab9e4b98136b76091a4a6d02d65ddb3612f21#egg=babel_yaml-master',
    'caveman==1.0',
    'cssmin==0.1.4',
    'docopt==0.6.2',
    'docutils==0.10',
    'ecdsa==0.13',
    'Fabric==1.11.1',
    'Flask==0.10.1',
    'Flask-Actions==0.6.6',
    'Flask-Assets==0.10',
    'Flask-Babel==0.9',
    'Flask-Cache==0.13.1',
    'Flask-Limiter==0.7.9',
    'flup==1.0.3.dev20110405',
    'gunicorn==0.17.2',
    'itsdangerous==0.24',
    'jedi==0.8.1',
    'Jinja2==2.7.3',
    'jsmin==2.1.1',
    'limits==1.0.6',
    'lxml==3.4.2',
    'MarkupSafe==0.23',
    'odict==1.5.1',
    'paramiko==1.17.0',
    'pexpect==2.4',
    'ply==3.4',
    'prompt-toolkit==0.20',
    'pycrypto==2.6.1',
    'Pygments==1.6',
    'python-memcached==1.53',
    'pytz==2014.10',
    'pywatch==0.4',
    'PyYAML==3.10',
    'requests==1.1.0',
    'simplejson==3.3.1',
    'six==1.8.0',
    'slimit==0.7.4',
    'speaklater==1.3',
    'Sphinx==1.2b1',
    'sphinxcontrib-httpdomain==1.1.8',
    'virtualenv==1.8.4',
    'wcwidth==0.1.1',
    'webassets==0.10.1',
    'Werkzeug==0.9.6',
    'sh==1.12.14',
]

setup_requirements = [
    # TODO(rtxanson): put setup requirements (distutils extensions, etc.) here
    'pip==8.1.2',
    'bumpversion==0.5.3',
    'wheel==0.29.0',
    'watchdog==0.8.3',
    'flake8==2.6.0',
    'tox==2.3.1',
    'coverage==4.1',
    'Sphinx==1.4.8',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='nds',
    version='1.0.0',
    description="Neahttadigisánit is a dictionary application that uses FSTs to provide smarter lookups",
    long_description=readme + '\n\n' + history,
    author="Ryan Johnson",
    author_email='ryan.txanson@gmail.com',
    url='https://giellatekno.uit.no',
    packages=find_packages(include=['neahtta']),
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'neahtta = neahtta.main:main'
        ]
    },
    keywords='nds',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
