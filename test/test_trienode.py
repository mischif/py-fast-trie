# encoding: utf-8

################################################################################
#                                 py-fast-trie                                 #
#          Python library for tries with different grades of fastness          #
#                            (C) 2020, Jeremy Brown                            #
#       Released under version 3.0 of the Non-Profit Open Source License       #
################################################################################

from py_fast_trie.x_fast import TrieNode

def test_init():
	left = TrieNode("left", True)
	right = TrieNode("right", True)
	par = TrieNode("parent", False, left, right)

	assert left._value == "left"
	assert left._leaf == True
	assert left._left is None
	assert left._right is None
	assert left._parent is None

	assert right._value == "right"
	assert right._leaf == True
	assert right._left is None
	assert right._right is None
	assert right._parent is None

	assert par._value == "parent"
	assert par._leaf == False
	assert par._left is left
	assert par._right is right
	assert par._parent is None

def test_properties():
	left = TrieNode(0, True)
	right = TrieNode(1, True)
	middle = TrieNode(0, False, left, right)
	root = TrieNode(None, False, middle)
	
	left.parent = middle
	left.right = right

	right.parent = middle
	right.left = left

	middle.parent = root

	assert left.leaf == True
	assert left.left is None
	assert left.right is right
	assert left.parent is middle
	assert left.value == 0
	assert left.value_bits == "00"
	assert str(left) == "0"

	assert right.leaf == True
	assert right.left is left
	assert right.right is None
	assert right.parent is middle
	assert right.value == 1
	assert right.value_bits == "01"
	assert str(right) == "1"

	assert middle.leaf == False
	assert middle.left is left
	assert middle.right is right
	assert middle.parent is root
	assert middle.value is 0
	assert middle.value_bits == "0"
	assert str(middle) == "0"

	assert root.leaf == False
	assert root.left is middle
	assert root.right is None
	assert root.parent is None
	assert root.value is None
	assert root.value_bits == ""
	assert str(root) == "Root"
