# encoding: utf-8

################################################################################
#                                 py-fast-trie                                 #
#          Python library for tries with different grades of fastness          #
#                            (C) 2020, Jeremy Brown                            #
#       Released under version 3.0 of the Non-Profit Open Source License       #
################################################################################

from __future__ import division

from sys import maxsize

from sortedcontainers import SortedList

from py_fast_trie import XFastTrie
from py_hopscotch_dict import HopscotchDict

class YFastTrie(object):

	@staticmethod
	def _calculate_representative(value, max_length):
		"""
		Calculate the smallest value that would exist in _partitions
		the given value could belong to

		:param val: The value to calculate the representative for
		:param max_length: The bit length of the largest possible representative

		:return: (int) The closest possible representative to the given number
		"""
		return min(max_length * (value // max_length) + (-1 % max_length), 2 ** max_length - 1)

	@staticmethod
	def _merge_subtrees(left_tree, right_tree, max_size):
		"""
		Combine the elements of two trees into one larger tree,
		splitting them again if the larger tree exceeds a given size

		:param left_tree: Tree containing smaller elements
		:param right_tree: Tree containing larger elements
		:param max_size: Maximum size the combined tree can be before splitting
		:return: (tuple) The combined tree and None if both trees' elements are
						 less than max_size, the tree with the smaller elements
						 and the tree with the larger elements otherwise
		"""
		if len(left_tree) + len(right_tree) <= max_size:
			left_tree.update(right_tree)
			result = (left_tree, None)
		else:
			total_median = (len(left_tree) + len(right_tree)) // 2 - 1
			if total_median < len(left_tree):
				total_median = left_tree[total_median]
			else:
				total_median = right_tree[total_median - len(left_tree)]

			# Taking advantage of the fact the number of elements in a subtree can only
			# be twice the bit length of the maximum element before splitting
			median_rep = YFastTrie._calculate_representative(total_median, max_size // 2)

			if median_rep <= max(left_tree):
				from_tree = left_tree
				to_tree = right_tree
				side = -1
			else:
				from_tree = right_tree
				to_tree = left_tree
				side = 0

			while max(left_tree) > median_rep or min(right_tree) <= median_rep:
				to_tree.add(from_tree.pop(side))

			result = (left_tree, right_tree)

		return result

	@staticmethod
	def _split_subtree(tree, max_length):
		"""
		Split a tree by its median element into two smaller trees

		:param tree: The tree to split
		:param max_length: The size of the largest possible element in the trie in bits
		:return: (tuple) The tree with the smaller elements,
						 and the tree with the larger elements
		"""
		median = tree.bisect_right(YFastTrie._calculate_representative(tree[len(tree) // 2], max_length))
		return SortedList(tree.islice(stop=median)), SortedList(tree.islice(start=median))

	def _get_value_subtree(self, value, create_subtree=False):
		"""
		Find the subtree that would hold the given value

		:param value: The value to find
		:param create_subtree: If there is no subtree that would hold the given value,
							   create one
		:return: (tuple) The subtree that potentially holds the given value,
						 and its corresponding representative
		"""
		result = None

		if self._count == 0:
			rep_node = None
		elif value <= self._min or self._min is None:
			rep_node = self._partitions.min_node
		else:
			# As the X-fast trie looks for strict successors,
			# if the value being searched for is a representative,
			# the wrong representative will be returned if the one being searched for
			# is not the largest, and no representative will be returned at all if it is;
			# so subtract one before searching for the successor
			rep_node = self._partitions.successor(value - 1)

		if rep_node is None:
			if create_subtree:
				rep = self._calculate_representative(value, self._maxlen)
				self._partitions += rep
				rep_node = self._partitions.successor(rep - 1)
				self._subtrees[rep] = result = SortedList()
		else:
			# Every representative in the X-fast trie should have a corresponding SortedList;
			# the code should blow up if it doesn't
			result = self._subtrees[rep_node.value]

		return (result, rep_node)

	def clear(self):
		"""
		Remove all values from the trie and return it to its starting state
		"""
		self._count = 0
		self._max = None
		self._min = None
		self._partitions = XFastTrie(self._maxlen)
		self._subtrees = HopscotchDict()

	def insert(self, value):
		"""
		Insert a value into the trie

		:param value: The value to insert into the trie
		"""
		value = XFastTrie._to_int(value, self._maxlen)
		subtree, rep_node = self._get_value_subtree(value, True)
		# Do nothing if the value is already in the trie
		if value in subtree:
			return

		if self._max is None or value > self._max:
			self._max = value

		if self._min is None or value < self._min:
			self._min = value

		subtree.add(value)

		if len(subtree) > self._max_subtree_size:
			# Out with the old
			del self._subtrees[rep_node.value]
			self._partitions -= rep_node.value

			# In with the new
			for tree in self._split_subtree(subtree, self._maxlen):
				rep = self._calculate_representative(max(tree), self._maxlen)
				self._partitions += rep
				self._subtrees[rep] = tree

		self._count += 1

	def predecessor(self, value):
		"""
		Find the largest value in the trie strictly less than the given value,
		if it exists

		:param value: The value to find the predecessor of
		:return: (int) The predecessor of the given value, or None if it doesn't exist
		"""
		value = XFastTrie._to_int(value, self._maxlen)
		subtree, rep_node = self._get_value_subtree(value)

		# subtree should be None only if the trie is empty
		if subtree is None and self._count == 0:
			raise ValueError(u"No values exist in trie")
		elif value <= self._min or self._min is None:
			return None
		elif value > self._max:
			return self._max

		if min(subtree) >= value:
			subtree = self._subtrees[rep_node.pred.value]

		return subtree[subtree.bisect_left(value) - 1]

	def remove(self, value):
		"""
		Remove the given value from the trie

		:param value: The value to remove from the trie
		"""
		value = XFastTrie._to_int(value, self._maxlen)
		subtree, rep_node = self._get_value_subtree(value)

		# There should be no subtree only if the given value is not in the trie
		if subtree is None or value not in subtree:
			raise ValueError(u"Value does not exist in trie")

		if self._min == value:
			if len(subtree) > 1:
				min_succ = subtree[1]
			else:
				min_succ = self.successor(value)
		else:
			min_succ = -1

		if self._max == value:
			if len(subtree) > 1:
				max_pred = subtree[-2]
			else:
				max_pred = self.predecessor(value)
		else:
			max_pred = -1

		if min_succ != -1:
			self._min = min_succ

		if max_pred != -1:
			self._max = max_pred

		subtree.remove(value)

		if len(subtree) == 0:
			del self._subtrees[rep_node.value]
			self._partitions -= rep_node.value

		elif len(subtree) < self._min_subtree_size and len(self._partitions) > 1:
			if rep_node.pred is not None:
				left_rep = rep_node.pred
				right_rep = rep_node
			else:
				left_rep = rep_node
				right_rep = rep_node.succ

			left_tree = self._subtrees[left_rep.value]
			right_tree = self._subtrees[right_rep.value]

			# Out with the old
			del self._subtrees[left_rep.value]
			del self._subtrees[right_rep.value]
			self._partitions -= left_rep.value
			self._partitions -= right_rep.value

			# In with the new
			for tree in filter(None, self._merge_subtrees(left_tree, right_tree, 2 * self._maxlen)):
				rep = self._calculate_representative(max(tree), self._maxlen)
				self._partitions += rep
				self._subtrees[rep] = tree

		self._count -= 1

	def successor(self, value):
		"""
		Find the smallest value in the trie strictly greater than the given value,
		if it exists

		:param value: The value to find the successor of
		:return: (int) The successor of the given value, or None if it doesn't exist
		"""
		value = XFastTrie._to_int(value, self._maxlen)
		subtree, rep_node = self._get_value_subtree(value)

		# subtree should be None only if the trie is empty
		if subtree is None and self._count == 0:
			raise ValueError(u"No values exist in trie")
		elif value >= self._max or self._max is None:
			return None
		elif value < self._min:
			return self._min

		if max(subtree) <= value:
			subtree = self._subtrees[rep_node.succ.value]

		return subtree[subtree.bisect_right(value)]

	@property
	def max(self):
		"""
		The maximum value in the trie

		:return: (int) The maximum value in the trie,
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
		return self._min

	def __init__(self, max_length=(maxsize.bit_length() + 1)):
		self._maxlen = max_length
		self._min_subtree_size = max_length // 2
		self._max_subtree_size = max_length * 2
		self.clear()

	def __contains__(self, value):
		value = XFastTrie._to_int(value, self._maxlen)
		subtree, _ = self._get_value_subtree(value)
		return subtree is not None and value in subtree

	def __gt__(self, value):
		value = XFastTrie._to_int(value, self._maxlen)
		return self.successor(value)

	def __iadd__(self, value):
		value = XFastTrie._to_int(value, self._maxlen)
		self.insert(value)
		return self

	def __isub__(self, value):
		value = XFastTrie._to_int(value, self._maxlen)
		self.remove(value)
		return self

	def __iter__(self):
		for rep in sorted(self._subtrees):
			for value in self._subtrees[rep]:
				yield value

	def __len__(self):
		return self._count

	def __lt__(self, value):
		value = XFastTrie._to_int(value, self._maxlen)
		return self.predecessor(value)
