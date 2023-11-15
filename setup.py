import os
import io
from setuptools import setup, find_packages


# Helpers
def read(*paths, required=True):
    """Read a text file."""
    try:
        basedir = os.path.dirname(__file__)
        fullpath = os.path.join(basedir, *paths)
        contents = io.open(fullpath, encoding='utf-8').read().strip()
        return contents
    except FileNotFoundError:
        return ''


# Prepare
PACKAGE = 'budgetkey_api'
NAME = 'budgetkey-api'
INSTALL_REQUIRES = read('requirements.txt').split('\n')
TESTS_REQUIRE = [
    'pylama',
    'pytest'
]
README = read('README.md', required=False)
VERSION = read(PACKAGE, 'VERSION')
PACKAGES = find_packages(exclude=['examples', 'tests'])


# Run
setup(
    name=NAME,
    version=VERSION,
    packages=PACKAGES,
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    extras_require={'develop': TESTS_REQUIRE},
    zip_safe=False,
    long_description=README,
    description='{{ DESCRIPTION }}',
    author='Adam Kariv',
    url='https://github.com/OpenBudget/budgetkey-api',
    license='MIT',
    keywords=[
        'data',
        'web'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
