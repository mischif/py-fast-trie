# encoding: utf-8

################################################################################
#                                 py-fast-trie                                 #
#          Python library for tries with different grades of fastness          #
#                            (C) 2020, Jeremy Brown                            #
#       Released under version 3.0 of the Non-Profit Open Source License       #
################################################################################

from io import open
from os.path import abspath, dirname, join
from setuptools import find_packages, setup


package_root = abspath(dirname(__file__))

# Get the long description from the README file
with open(join(package_root, "README.md"), encoding="utf-8") as desc:
	long_description = desc.read()


setup(
	name="py-fast-trie",

	packages=find_packages(where="src"),

	package_dir={"": "src"},

	license="NPOSL-3.0",

	url="https://github.com/mischif/py-fast-trie",

	description="Python library for tries with different grades of fastness",

	long_description=long_description,
	long_description_content_type="text/markdown",

	author="Jeremy Brown",
	author_email="mischif@users.noreply.github.com",

	python_requires="~=3.6",

	package_data={"py_fast_trie": ["VERSION"]},

	install_requires=["py-hopscotch-dict", "sortedcontainers"],
	
	setup_requires=["pytest-runner", "setuptools_scm"],

	tests_require=["hypothesis", "hypothesis-pytest", "pytest", "pytest-cov"],

	zip_safe=False,

	keywords=["x-fast", "y-fast", "trie", "data structures"],

	extras_require={
		"test": ["codecov"],
		},

	options={
		"aliases": {
			"test": "pytest",
			},

		"metadata": {
			"license_files": "LICENSE",
			},
		},

	classifiers=[
		"Development Status :: 5 - Production/Stable",

		"Operating System :: OS Independent",

		"License :: OSI Approved :: Open Software License 3.0 (OSL-3.0)",

		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.8",

		"Topic :: Software Development :: Libraries",
		"Topic :: Software Development :: Libraries :: Python Modules",
		],
	)
