#!/usr/bin/env python
from setuptools import find_namespace_packages, setup
import os
import re

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md')) as f:
    long_description = f.read()


package_name = "dbt-watsonx-presto"


# get this from a separate file
def _dbt_presto_version():
    _version_path = os.path.join(
        this_directory, 'dbt', 'adapters', 'presto', '__version__.py'
    )
    _version_pattern = r'''version\s*=\s*["'](.+)["']'''
    with open(_version_path) as f:
        match = re.search(_version_pattern, f.read().strip())
        if match is None:
            raise ValueError(f'Invalid version at {_version_path}')
        return match.group(1)


package_version = _dbt_presto_version()
description = """The Presto adapter plugin for dbt (data build tool)"""

setup(
    name=package_name,
    version=package_version,

    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='IBM watsonx.data',

    packages=find_namespace_packages(include=['dbt', 'dbt.*']),
    package_data={
        'dbt': [
            'include/presto/dbt_project.yml',
            'include/presto/sample_profiles.yml',
            'include/presto/macros/*.sql',
            'include/presto/macros/*/*.sql',
        ]
    },
    install_requires=[
        'dbt-core~=1.8',
        'presto-python-client==0.8.4',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
