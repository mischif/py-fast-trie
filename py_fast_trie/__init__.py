# encoding: utf-8

################################################################################
#                                 py-fast-trie                                 #
#          Python library for tries with different grades of fastness          #
#                            (C) 2020, Jeremy Brown                            #
#       Released under version 3.0 of the Non-Profit Open Source License       #
################################################################################

from io import open
from os.path import abspath, dirname, join

from py_fast_trie.x_fast import XFastTrie
from py_fast_trie.y_fast import YFastTrie

module_root = dirname(abspath(__file__))

with open(join(module_root, "VERSION"), encoding="utf-8") as version_file:
	__version__ = version_file.read().strip()
