from setuptools import setup, find_packages

setup(
    name="reny",
    version="1.0.0",
    description="A lightweight, powerful batch renaming and filesystem organizing CLI tool.",
    packages=find_packages(),
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
