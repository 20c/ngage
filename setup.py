from setuptools import setup, find_packages

version = open("facsimile/VERSION").read().strip()
requirements = open("facsimile/requirements.txt").read().split("\n")
test_requirements = open("facsimile/requirements-test.txt").read().split("\n")

setup(
    name="ngage",
    version=version,
    author="20C",
    author_email="code@20c.com",
    description="network device config twirler",
    long_description="",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    test_requires=test_requirements,
    entry_points={"console_scripts": ["ngage=ngage.cli:cli",]},
    zip_safe=True,
)
