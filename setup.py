# encoding: utf-8

################################################################################
#                                 py-fast-trie                                 #
#          Python library for tries with different grades of fastness          #
#                            (C) 2020, Jeremy Brown                            #
#       Released under version 3.0 of the Non-Profit Open Source License       #
################################################################################

# Have to enable user site manually since PEP517 workflow doesn't support editable installs
# See pypa/pip#7953 
import site
import sys

from setuptools import setup

site.ENABLE_USER_SITE = "--user" in sys.argv[1:]

if __name__ == "__main__":
	setup()
