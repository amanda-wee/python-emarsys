#!/usr/bin/env python
from setuptools import setup, find_packages

import emarsys

CLASSIFIERS = ["Development Status :: 2 - Pre-Alpha",
               "Intended Audience :: Developers",
               "License :: OSI Approved :: Apache Software License",
               "Natural Language :: English",
               "Operating System :: OS Independent",
               "Programming Language :: Python",
               "Topic :: Software Development :: Libraries :: Python Modules"]

KEYWORDS = "emarsys api wrapper"

REPO_URL = "https://github.com/eugene-wee/python-emarsys"

setup(name="python-emarsys",
      version=emarsys.__version__,
      description="""Emarsys REST API wrapper for Python.""",
      author=emarsys.__author__,
      url=REPO_URL,
      packages=find_packages(),
      download_url=REPO_URL + "/tarball/master",
      classifiers=CLASSIFIERS,
      keywords=KEYWORDS,
      zip_safe=True,
      install_requires=["distribute"])
