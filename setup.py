import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="reny",
    version="1.0.5",
    description="A lightweight, powerful batch renaming and filesystem organizing CLI tool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={'reny': ['cli/base/*.template']},
    install_requires=['pygtrie'],
    extras_require={
        "test": ["pytest", "pytest-mock"]
    },
    entry_points={
        'console_scripts': [
            'reny=reny.cli.renamer.renamer_dispatch:main',
        ],
    },
)
