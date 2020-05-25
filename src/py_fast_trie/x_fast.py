# encoding: utf-8

################################################################################
#                                 py-fast-trie                                 #
#          Python library for tries with different grades of fastness          #
#                            (C) 2020, Jeremy Brown                            #
#       Released under version 3.0 of the Non-Profit Open Source License       #
################################################################################

from __future__ import division

from numbers import Integral
from sys import maxsize

from py_hopscotch_dict import HopscotchDict

try:
	from future_builtins import map
except ImportError:
	pass


class TrieNode(object):
	def _get_leaf(self):
		"""
		Indicated whether or not the node is a leaf

		:return: (bool) Whether or not the node is a leaf
		"""
		return self._leaf

	def _get_left(self):
		"""
		The left child of the current node -
		its predecessor if the current node is a leaf,
		its left child if the current node is an internal node with such,
		a descendant pointer if the current node is an internal node with no child

		:return: (TrieNode) The current node's left child,
							None if the current node is the smallest leaf
		"""
		return self._left

	def _get_parent(self):
		"""
		The parent of the current node

		:return: (TrieNode) The current node's parent,
							None if the current node is the root
		"""
		return self._parent

	def _get_right(self):
		"""
		The right child of the current node -
		its successor if the current node is a leaf,
		its right child if the current node is an internal node with such,
		a descendant pointer if the current node is an internal node with no child

		:return: (TrieNode) The current node's right child,
							None if the current node is the largest leaf
		"""
		return self._right

	def _get_value(self):
		"""
		The value of the current node, expressed as an integer

		:return: (int) The current node's value
		"""
		return self._value

	def _get_value_bitstring(self):
		"""
		The value of the current node, expressed as a string of 1s and 0s

		:return: (str) The current node's value, as bits
		"""
		node = self
		result = []

		while node.value is not None:
			result.append(str(node.value & 1))
			node = node.parent

		return "".join(reversed(result))

	def _set_left(self, new_left):
		"""
		Sets the left child of the current node

		:param new_left: (TrieNode) The current node's left child, or None
		"""
		self._left = new_left

	def _set_parent(self, new_parent):
		"""
		Sets the parent of the current node

		:param new_parent: (TrieNode) The current node's parent, or None
		"""
		self._parent = new_parent

	def _set_right(self, new_right):
		"""
		Sets the left child of the current node

		:param new_right: (TrieNode) The current node's right child, or none
		"""
		self._right = new_right

	leaf = property(_get_leaf)
	value = property(_get_value)
	value_bits = property(_get_value_bitstring)
	parent = property(_get_parent, _set_parent)
	left = property(_get_left, _set_left)
	right = property(_get_right, _set_right)
	pred = property(_get_left, _set_left)
	succ = property(_get_right, _set_right)

	def __init__(self, value, leaf, left=None, right=None):
		self._leaf = leaf
		self._value = value
		self._left = left
		self._right = right
		self._parent = None

	def __str__(self):
		return "Root" if self._value is None else str(self._value)


class XFastTrie(object):
	@staticmethod
	def _make_level_tables(levels):
		"""
		Creates the dicts used when searching for a value in the trie

		:param levels: (int) The number of levels in the trie
		:return: (list) search structures for each level of the trie
		"""
		return [HopscotchDict() for _ in range(levels)]

	@staticmethod
	def _to_int(value, length):
		"""
		Confirm the desired value could be contained in the table,
		then perform any necessary conversions to the canonical value format

		:param value: (int/bytes) The value to be converted
		:param length: The maximum bit length of a value in the trie
		:return: (int) The value converted to an int
		"""
		if isinstance(value, Integral):
			if value.bit_length() > length:
				raise ValueError(u"Value is too big to be stored in trie")
			elif value < 0:
				raise ValueError(u"Negative values cannot be stored in trie")
			else:
				return value

		elif isinstance(value, bytes):
			if len(value) * 8 > length:
				raise ValueError(u"Value is too big to be stored in trie")

			else:
				return sum(map(lambda t: t[1] << 8 * t[0], enumerate(reversed(value))))

		else:
			raise TypeError(u"Only integers and byte sequences can be stored in trie")

	def _get_closest_ancestor(self, value):
		"""
		Find the node in the trie with the longest prefix that matches the given value

		:param value: (int) The value to search for
		:return: (TrieNode, int) The node with the longest prefix matching the given value,
								 and its depth in the trie
		"""
		result = self._root
		result_level = -1

		low_side = 0
		high_side = self._maxlen - 1

		while low_side <= high_side:
			level = (low_side + high_side) // 2
			prefix = value >> (self._maxlen - level - 1)

			if prefix not in self._level_tables[level]:
				high_side = level - 1
			else:
				result = self._level_tables[level][prefix]
				result_level = level
				low_side = level + 1

		return (result, result_level)

	def _get_closest_leaf(self, value):
		"""
		Find the leaf in the trie with the value closest to the given value

		:param value: (int) The value to search for
		:return: (TrieNode) The leaf with the closest value to the given value
		"""
		result = None
		ancestor, level = self._get_closest_ancestor(value)

		# The value is stored in the trie and therefore is the closest leaf to itself
		if ancestor.leaf:
			return ancestor

		# The pointer to the next level down is a descendant pointer
		# and may be larger or smaller than the given value, depending on the leg
		else:
			direction = value >> (self._maxlen - level - 2) & 1
			descendant = ancestor.left if direction == 0 else ancestor.right

			if descendant is not None:
				# The descendant pointer only points to values on the other leg of the ancestor;
				# make sure there is no leaf not a child of the ancestor which is closer
				candidate = descendant.pred if direction == 0 else descendant.succ

				if candidate is None or abs(descendant.value - value) < abs(candidate.value - value):
					result =  descendant
				else:
					result = candidate
		return result

	def clear(self):
		"""
		Empty the trie of all values
		"""
		self._level_tables = self._make_level_tables(self._maxlen)
		self._root = TrieNode(None, False)
		self._count = 0
		self._min = None
		self._max = None

	def insert(self, value):
		"""
		Add the given value to the trie

		:param value: (int/bytes) The value to add to the trie
		"""
		value = self._to_int(value, self._maxlen)

		# Do nothing if the value is already in the trie
		if value in self._level_tables[-1]:
			return

		leaf_pred = self.predecessor(value) if self._count > 0 else None
		leaf_succ = self.successor(value) if self._count > 0 else None
		leaf_node = TrieNode(value, True, leaf_pred, leaf_succ)

		# Wire the new leaf into the linked list and add to the leaf dict
		self._level_tables[-1][value] = leaf_node

		if leaf_pred is not None:
			leaf_pred.succ = leaf_node

		if leaf_succ is not None:
			leaf_succ.pred = leaf_node

		# Update global min/max pointers as necessary
		if self._min is None or value < self._min.value:
			self._min = leaf_node

		if self._max is None or value > self._max.value:
			self._max = leaf_node

		# Walk up the trie from the leaf node, creating internal nodes as necessary
		last_inserted = leaf_node
		for level in reversed(range(self._maxlen - 1)):
			node_value = int(value >> (self._maxlen - level - 1))
			node = self._level_tables[level].get(node_value)

			if node is None:
				# Determine which leg the last node inserted into the trie was on relative the one to be created,
				# and find the corresponding leaf to use for the descendant pointer
				last_inserted_leg = last_inserted.value & 1
				descendant_direction = "right" if last_inserted_leg == 0 else "left"
				descendant = last_inserted
				while not descendant.leaf:
					# If this loop ends up following a descendant pointer,
					# it means there was no intermediate node to follow instead;
					# a pointer on the left leg would lead to the smallest leaf of the node's right subtree,
					# which would also be the smallest leaf of the original node and the desired node,
					# and likewise for a descendant pointer on the right leg.
					descendant = getattr(descendant, descendant_direction)

				if last_inserted_leg == 0:
					node_left = last_inserted
					node_right = descendant
				else:
					node_right = last_inserted
					node_left = descendant

				# Create the new node, insert it into its respective dict and update pointers
				node = TrieNode(node_value, False, node_left, node_right)
				self._level_tables[level][node_value] = node
				last_inserted.parent = node
				last_inserted = node
			else:
				# Update the last node that was inserted to point to its newly-found parent
				if last_inserted.parent is None:
					last_inserted.parent = node

				# Update the current node to know about its potential children
				left_child_value = node.value << 1 & -2
				right_child_value = node.value << 1 | 1
				left_child = self._level_tables[level + 1].get(left_child_value)
				right_child = self._level_tables[level + 1].get(right_child_value)

				if node.left is left_child:
					pass
				elif left_child is not None:
					node.left = left_child
				else:
					if node.left.value > value:
						node.left = leaf_node

				if node.right is right_child:
					pass
				elif right_child is not None:
					node.right = right_child
				else:
					if node.right.value < value:
						node.right = leaf_node

		if self._root.left is None or self._root.left.leaf:
			root_left = self._level_tables[0].get(0)
			self._root.left = root_left or self._min
			if root_left is not None:
				root_left.parent = self._root

		if self._root.right is None or self._root.right.leaf:
			root_right = self._level_tables[0].get(1)
			self._root.right = root_right or self._max
			if root_right is not None:
				root_right.parent = self._root

		self._count += 1

	def predecessor(self, value):
		"""
		Find the largest value in the trie strictly less than the given value

		:param value: (int) The value to find the predecessor for
		:return: (TrieNode) The leaf with the largest value strictly less than the given value,
							or None if the value is at most the value of the smallest leaf
		"""
		value = self._to_int(value, self._maxlen)
		node = self._get_closest_leaf(value)

		# This should only happen if there are no values in the trie,
		# But if it could also happen because of some unconsidered edge case,
		# make some noise so the edge case can be fixed
		if node is None:
			raise ValueError(u"No values exist in trie")
		else:
			return node.pred if node.value >= value else node

	def remove(self, value):
		"""
		Remove the given value from the trie

		:param value: (int/bytes) The value to remove from the trie
		"""
		value = self._to_int(value, self._maxlen)

		# Error when trying to remove a value that hasn't been added
		if value not in self._level_tables[-1]:
			raise ValueError(u"Value does not exist in trie")
		else:
			node = self._level_tables[-1][value]
			leaf_pred = node.pred
			leaf_succ = node.succ

			# Take the value out of the leaf dict and linked list
			del self._level_tables[-1][value]

			if leaf_pred is not None:
				leaf_pred.succ = leaf_succ

			if leaf_succ is not None:
				leaf_succ.pred = leaf_pred

			# Update global min/max pointers as necessary
			if self._min is node:
				self._min = leaf_succ

			if self._max is node:
				self._max = leaf_pred

			# Walk up the trie from the leaf node, modifying/removing internal nodes as necessary
			node = node.parent
			level = self._maxlen - 2
			while node.value is not None:
				left_child_value = node.value << 1 & -2
				right_child_value = node.value << 1 | 1
				left_child = self._level_tables[level + 1].get(left_child_value)
				right_child = self._level_tables[level + 1].get(right_child_value)

				# Node has no children, delete it
				if left_child is None and right_child is None:
					del self._level_tables[level][node.value]

				else:
					descendant = left_child if right_child is None else right_child
					leg = "right" if right_child is None else "left"
					while not descendant.leaf:
						# If this loop ends up following a descendant pointer,
						# it means there was no intermediate node to follow instead;
						# a pointer on the left leg would lead to the smallest leaf of the node's right subtree,
						# which would also be the smallest leaf of the original node and the desired node,
						# and likewise for a descendant pointer on the right leg.
						descendant = getattr(descendant, leg)

					if left_child is None:
						node.left = descendant

					elif right_child is None:
						node.right = descendant

				node = node.parent
				level -= 1

		root_left = self._level_tables[0].get(0)
		root_right = self._level_tables[0].get(1)

		# Update root
		if root_left is None and root_right is None:
			self._root.left = self._root.right = None

		elif root_left is None:
			self._root.left = self._min

		elif root_right is None:
			self._root.right = self._max

		self._count -= 1

	def successor(self, value):
		"""
		Find the smallest value in the trie strictly greater than the given value

		:param value: (int) The value to find the successor for
		:return: (TrieNode) The leaf with the smallest value strictly greater than the given value,
							or None if the value is at least the value of the largest leaf
		"""
		value = self._to_int(value, self._maxlen)
		node = self._get_closest_leaf(value)

		# This should only happen if there are no values in the trie,
		# But if it could also happen because of some unconsidered edge case,
		# make some noise so the edge case can be fixed
		if node is None:
			raise ValueError(u"No values exist in trie")
		else:
			return node.succ if node.value <= value else node

	@property
	def max(self):
		"""
		The maximum value in the trie

		:return: (int) The maximum value in the trie,
					   or None if the trie is empty
		"""
		return self._max.value

	@property
	def max_node(self):
		"""
		The node related to the maximum value in the trie

		:return: (TrieNode) The maximum value in the trie,
							or None if the trie is empty
		"""
		return self._max

	@property
	def min(self):
		"""
		The minimum value in the trie

		:return: (int) The minimum value in the trie,
					   or None if the trie is empty
		"""
		return self._min.value

	@property
	def min_node(self):
		"""
		The node related to the minimum value in the trie

		:return: (TrieNode) The minimum value in the trie,
							or None if the trie is empty
		"""
		return self._min

	def __init__(self, max_length=(maxsize.bit_length() + 1)):
		self._maxlen = max_length
		self.clear()

	def __contains__(self, value):
		value = self._to_int(value, self._maxlen)
		return value in self._level_tables[-1]

	def __gt__(self, value):
		value = self._to_int(value, self._maxlen)
		result = self.successor(value)
		return result.value if result is not None else result

	def __iadd__(self, value):
		value = self._to_int(value, self._maxlen)
		self.insert(value)
		return self

	def __isub__(self, value):
		value = self._to_int(value, self._maxlen)
		self.remove(value)
		return self

	def __iter__(self):
		node = self._min
		while node is not None:
			yield node.value
			node = node.succ

	def __len__(self):
		return self._count

	def __lt__(self, value):
		value = self._to_int(value, self._maxlen)
		result = self.predecessor(value)
		return result.value if result is not None else result
