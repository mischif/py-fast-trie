# encoding: utf-8

################################################################################
#                                 py-fast-trie                                 #
#          Python library for tries with different grades of fastness          #
#                            (C) 2020, Jeremy Brown                            #
#       Released under version 3.0 of the Non-Profit Open Source License       #
################################################################################

from __future__ import division

from itertools import chain
from random import randint

import pytest

from hypothesis import given, settings
from hypothesis.strategies import integers, lists
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule
from sortedcontainers import SortedList

from py_fast_trie import YFastTrie
from test import (invalid_trie_entry,
				  max_trie_entry_size,
				  max_trie_value,
				  valid_int_entries,
				  valid_int_entry,
				  valid_trie_entries,
				  valid_trie_entry,
				  XFastTrie
				  )


@given(integers(min_value=0, max_value=max_trie_value))
def test_calculate_representative(val):
	rep = YFastTrie._calculate_representative(val, max_trie_entry_size)
	assert rep >= val
	assert (rep + 1) % max_trie_entry_size == 0


@given(lists(valid_int_entry, min_size=2, max_size=((4 * max_trie_entry_size) - 1), unique=True))
def test_merge_subtrees(values):
	values = SortedList(values)
	split = randint(1, len(values) - 1)
	left_tree = SortedList(values.islice(stop=split))
	right_tree = SortedList(values.islice(start=split))
	new_left, new_right = YFastTrie._merge_subtrees(left_tree, right_tree, 2 * max_trie_entry_size)

	if len(values) <= 2 * max_trie_entry_size:
		assert new_right is None
		assert isinstance(new_left, SortedList)
		assert len(new_left) == len(values)
	else:
		assert isinstance(new_left, SortedList)
		assert isinstance(new_right, SortedList)
		assert len(new_left) + len(new_right) == len(values)
		assert YFastTrie._calculate_representative(max(new_left), max_trie_entry_size) < min(new_right)


@given(lists(valid_int_entry, min_size=((2 * max_trie_entry_size) + 1), max_size=((4 * max_trie_entry_size) - 1), unique=True))
def test_merge_large_subtrees(values):
	values = SortedList(values)
	split = len(values) // 2
	left_tree = SortedList(values.islice(stop=split))
	right_tree = SortedList(values.islice(start=split))
	new_left, new_right = YFastTrie._merge_subtrees(left_tree, right_tree, 2 * max_trie_entry_size)
	assert isinstance(new_left, SortedList)
	assert isinstance(new_right, SortedList)
	assert len(new_left) + len(new_right) == len(values)
	assert YFastTrie._calculate_representative(max(new_left), max_trie_entry_size) < min(new_right)

	split += 1
	left_tree = SortedList(values.islice(stop=split))
	right_tree = SortedList(values.islice(start=split))
	new_left, new_right = YFastTrie._merge_subtrees(left_tree, right_tree, 2 * max_trie_entry_size)
	assert isinstance(new_left, SortedList)
	assert isinstance(new_right, SortedList)
	assert len(new_left) + len(new_right) == len(values)
	assert YFastTrie._calculate_representative(max(new_left), max_trie_entry_size) < min(new_right)


@given(lists(valid_int_entry, min_size=((2 * max_trie_entry_size) + 1), max_size=((4 * max_trie_entry_size) - 1), unique=True))
def test_split_subtree(values):
	left_tree, right_tree = YFastTrie._split_subtree(SortedList(values), max_trie_entry_size)

	assert isinstance(left_tree, SortedList)
	assert isinstance(right_tree, SortedList)
	assert len(left_tree) + len(right_tree) == len(values)
	assert max(left_tree) < min(right_tree)
	assert YFastTrie._calculate_representative(max(left_tree), max_trie_entry_size) < min(right_tree)


@given(valid_trie_entries, valid_int_entries)
def test_get_value_subtree(entries, test_values):
	t = YFastTrie(max_trie_entry_size)

	assert t._get_value_subtree(test_values[0]) == (None, None)

	for entry in entries:
		t += entry

	entries = [XFastTrie._to_int(e, t._maxlen) for e in entries]

	for val in test_values:
		tree, rep_node = t._get_value_subtree(val)

		if val > t._partitions.max:
			assert tree is None
			assert rep_node is None

		else:
			assert val <= rep_node.value

			if val in entries:
				assert val in tree
			else:
				assert val not in tree


@given(valid_trie_entries, valid_int_entries)
def test_predecessor(entries, test_values):
	t = YFastTrie(max_trie_entry_size)

	for entry in entries:
		t += entry

	for val in test_values:
		pred = t < val

		if pred is not None:
			assert pred < val

			tree, _ = t._get_value_subtree(val)
			if tree is None or min(tree) >= val:
				tree, _ = t._get_value_subtree(pred)

			assert max([v for v in tree if v < val]) == pred

		else:
			assert val <= t.min


@given(valid_trie_entries, valid_int_entries)
def test_successor(entries, test_values):
	t = YFastTrie(max_trie_entry_size)

	for entry in entries:
		t += entry

	for val in test_values:
		succ = t > val

		if succ is not None:
			assert succ > val

			tree, _ = t._get_value_subtree(val)
			if tree is None or max(tree) <= val:
				tree, _ = t._get_value_subtree(succ)

			assert min([v for v in tree if v > val]) == succ

		else:
			assert val >= t.max


def test_successor_predecessor_empty_trie():
	t = YFastTrie(max_trie_entry_size)

	with pytest.raises(ValueError):
		t.successor(0)

	with pytest.raises(ValueError):
		t.predecessor(0)


@given(valid_trie_entries)
def test_clear(entries):
	t = YFastTrie(max_trie_entry_size)

	for entry in entries:
		t += entry

	assert len(t) > 0
	assert t.min is not None
	assert t.max is not None

	t.clear()

	assert len(t) == 0
	assert len(t._partitions) == 0
	assert len(t._subtrees) == 0
	assert t.min is None
	assert t.max is None


def test_insert_with_split():
	t = YFastTrie(max_trie_entry_size)

	big_rep = 3 * max_trie_entry_size - 1
	small_rep = 2 * max_trie_entry_size - 1
	for i in range(3 * max_trie_entry_size - 1, max_trie_entry_size - 1, -1):
		t += i

	assert len(t._partitions) == 1
	assert big_rep in t._subtrees
	assert len(t._subtrees[big_rep]) == 2 * max_trie_entry_size

	t += max_trie_entry_size - 1

	assert len(t._partitions) == 2
	assert big_rep in t._subtrees
	assert small_rep in t._subtrees
	assert len(t._subtrees[big_rep]) == max_trie_entry_size
	assert len(t._subtrees[small_rep]) == max_trie_entry_size + 1


@given(lists(valid_int_entry, min_size=0, max_size=max_trie_value, unique=True))
def test_iter(entries):
	t = YFastTrie(max_trie_entry_size)

	for entry in entries:
		t += entry

	entries = sorted(entries)

	for entry in t:
		assert entry == entries.pop(0)

	assert len(entries) == 0


class YFastStateMachine(RuleBasedStateMachine):
	def __init__(self):
		super(YFastStateMachine, self).__init__()
		self.t = YFastTrie(max_trie_entry_size)

	def teardown(self):
		values = list(chain.from_iterable(self.t._subtrees.values()))

		for val in values:
			self.t -= val

	@invariant()
	def valid_count(self):
		tree_sizes = map(lambda t: len(t), self.t._subtrees.values())
		assert len(self.t) == sum(tree_sizes)

	@invariant()
	def valid_min(self):
		if len(self.t) == 0:
			assert self.t.min is None
		elif len(self.t) == 1:
			assert self.t.min == self.t.max
		else:
			for value in chain.from_iterable(self.t._subtrees.values()):
				assert value is self.t.min or self.t.min < value

	@invariant()
	def valid_max(self):
		if len(self.t) == 0:
			assert self.t.max is None
		elif len(self.t) == 1:
			assert self.t.max == self.t.min
		else:
			for value in chain.from_iterable(self.t._subtrees.values()):
				assert value is self.t.min or self.t.min < value

	@invariant()
	def valid_representatives(self):
		rep = self.t._partitions.min_node
		while rep is not None:
			pred = rep.pred
			succ = rep.succ

			max(self.t._subtrees[rep.value]) <= rep.value

			if pred is not None:
				max(self.t._subtrees[pred.value]) < min(self.t._subtrees[rep.value])

			if succ is not None:
				min(self.t._subtrees[succ.value]) > max(self.t._subtrees[rep.value])

			rep = rep.succ

	@invariant()
	def valid_subtree_values(self):
		for rep in self.t._subtrees.keys():
			assert rep in self.t._partitions
			assert YFastTrie._calculate_representative(rep, max_trie_entry_size) == rep

	@rule(val=valid_trie_entry)
	def insert_value(self, val):
		self.t += val

	@rule(val=valid_trie_entry)
	def remove_value(self, val):
		if val not in self.t:
			try:
				self.t -= val
			except ValueError:
				pass
		else:
			self.t -= val

YFastStateMachine.TestCase.settings = settings(max_examples=50, deadline=None)
test_y_fast_trie = YFastStateMachine.TestCase
