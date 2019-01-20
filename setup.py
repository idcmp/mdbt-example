import os.path as p

import setuptools
from setuptools import setup

version = '1.0.0'

install_requires = []
try:
    with open(p.join(p.dirname(__file__), 'requirements', 'package.txt'), 'r') as reqs:
        for line in reqs:
            if not line.strip().startswith('--'):
                install_requires.append(line.strip())
except IOError:
    pass

tests_require = []
try:
    with open(p.join(p.dirname(__file__), 'requirements', 'test.txt'), 'r') as reqs:
        for line in reqs:
            if not line.strip().startswith('--'):
                tests_require.append(line.strip())
except IOError:
    pass

setup(
    name='mdbt',
    version=version,
    author='JAmes Atwill',
    author_email='james.atwill@globalrelay.net',
    url='TBD',
    description='..',
    long_description=open('README.md').read(),

    install_requires=install_requires,
    tests_require=tests_require,

    packages=setuptools.find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'mdbt = mdbt.main:main'
        ],
    },
)
