
from setuptools import setup, find_packages

version = open('facsimile/VERSION').read().strip()
requirements = open('facsimile/requirements.txt').read().split("\n")
test_requirements = open('facsimile/requirements-test.txt').read().split("\n")

setup(
    name='ngage',
    version=version,
    author='20C',
    author_email='code@20c.com',
    description='',
    long_description=open('README.txt').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
    ],

    packages=[
        'ngage',
    ],

    install_requires=requirements,
    test_requires=test_requirements,

    entry_points='''
        [console_scripts]
        ngage=ngage.cli:cli
    ''',

#    packages=['uixauto'],
#    namespace_packages=['twentyc'],

    zip_safe=True,
)
