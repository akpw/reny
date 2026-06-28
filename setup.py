import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="reny",
    version="1.0.6",
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
    url='https://github.com/akpw/reny',
    author='Arseniy Kuznetsov',
    author_email='k.arseniy@gmail.com',
    license='GNU General Public License v2 (GPLv2)',
    keywords='Batch Rename Organizer File System Management',
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Customer Service',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Operating System :: POSIX :: Linux',
        'Topic :: System',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'
    ],
)
