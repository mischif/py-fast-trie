py-fast-trie
============

[![Travis](https://img.shields.io/travis/mischif/py-fast-trie.svg?style=for-the-badge)](https://travis-ci.org/mischif/py-fast-trie)
[![Codecov](https://img.shields.io/codecov/c/github/mischif/py-fast-trie.svg?style=for-the-badge)](https://codecov.io/gh/mischif/py-fast-trie)
[![Python Versions](https://img.shields.io/pypi/pyversions/py-fast-trie?style=for-the-badge)](https://pypi.org/project/py-fast-trie/)
[![Package Version](https://img.shields.io/pypi/v/py-fast-trie?style=for-the-badge)](https://pypi.org/project/py-fast-trie/)
[![License](https://img.shields.io/pypi/l/py-fast-trie?style=for-the-badge)](https://pypi.org/project/py-fast-trie/)

py-fast-trie is a package that contains pure-Python implementations of an [X-fast Trie](https://en.wikipedia.org/wiki/X-fast_trie) and a [Y-fast trie](https://en.wikipedia.org/wiki/Y-fast_trie), as described in the [foundational paper](https://sci-hub.tw/10.1016/0020-0190%2883%2990075-3).

The most notable benefit of X-fast and Y-fast tries compared to more common data structures such as binary search trees is that searches are log-logarithmic in the cardinality of the universe as opposed to being logarithmic in the number of elements in the structure itself; For reference if you needed to store 2^20 items with a potential maximum value of 2^32 - 1, finding a particular item would take 20 operations in a red/black or AVL tree, but only 5 with an X-fast or Y-fast trie.

Usage
-----

The interfaces of the X-fast and Y-fast tries are identical, the Y-fast trie is used here as an example.

	>>> from py_fast_trie import YFastTrie
	>>> t = YFastTrie(max_length=32)		# The library defaults to the machine's word size
	>>> for i in range(10, 13):
	...     t += i					# Value insertion/removal operations have intuitive
	>>> t.min					# shorthands
	10
	>>> t += b'\x0d'				# The library can handle byte strings less than the
	>>> t.max					# max length by treating them as integers
	12
	>>> for val in t:
	...     print val
	10
	11
	12
	13
	>>> t < 12					# Predecessor/successor queries have intuitive
	11						# shorthands
	>>> t > 0
	10
	t -= 13
	>>> t > 12
	>>>
