#!/usr/bin/env python

"""traffic-control setup script"""

from distutils.core import setup, Extension

# make pyflakes happy
__pkgname__ = None
__version__ = None
exec(open("pytc/version.py").read())

# build/install python-tc
setup(
    name=__pkgname__,
    version=__version__,
    description="Python module for Traffic-Control",
    author="Piotr Gawlowicz",
    author_email="gawlowicz@tu-berlin.de",
    url="",
    packages=["pytc"],
    package_dir={"pytc": "pytc"},
    ext_modules=[],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Networking :: Firewalls",
        "Topic :: System :: Systems Administration",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
    license="Apache License, Version 2.0",
)
