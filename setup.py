
from setuptools import setup, find_packages

version = open('facsimile/VERSION').read().strip()
requirements = open('facsimile/requirements.txt').read().split("\n")
test_requirements = open('facsimile/requirements-test.txt').read().split("\n")

setup(
    name='ngage',
    version=version,
    author='20C',
    author_email='code@20c.com',
    description='network device config twirler',
    long_description='',
    classifiers=[
        'Development Status :: 4 - Beta',
    ],

    packages=find_packages(),
    include_package_data=True,

    install_requires=requirements,
    test_requires=test_requirements,

    entry_points={
        'console_scripts': [
            'ngage=ngage.cli:cli',
        ]
    },

    zip_safe=True,
)
