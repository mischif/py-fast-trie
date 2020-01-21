# encoding: utf-8

################################################################################
#                                 py-fast-trie                                 #
#          Python library for tries with different grades of fastness          #
#                            (C) 2020, Jeremy Brown                            #
#       Released under version 3.0 of the Non-Profit Open Source License       #
################################################################################

from struct import pack, unpack
from sys import maxsize

import pytest

from hypothesis import given, note, seed
from hypothesis.strategies import integers, lists
from hypothesis.stateful import RuleBasedStateMachine, invariant, precondition, rule

from py_fast_trie import XFastTrie
from test import (invalid_trie_entry,
				  max_trie_entry_size,
				  valid_int_entries,
				  valid_trie_entries,
				  valid_trie_entry)


def to_bytes(val):
	if val.bit_length() < 9:
		fmt = "B"
	elif val.bit_length() < 17:
		fmt = ">H"
	elif val.bit_length() < 33:
		fmt = ">L"
	else:
		fmt = ">Q"

	return pack(fmt, val)


@given(integers(min_value=0, max_value=max_trie_entry_size))
def test_make_level_tables(depth):
	assert len(XFastTrie._make_level_tables(depth)) == depth


@given(valid_trie_entry)
def test_to_int(value):
	if isinstance(value, int):
		assert XFastTrie._to_int(value, max_trie_entry_size) == value

	elif isinstance(value, bytes):
		value_int = unpack(">Q", value.rjust((maxsize.bit_length() + 1) / 8, b'\x00'))[0]
		assert XFastTrie._to_int(value, max_trie_entry_size) == value_int


@given(invalid_trie_entry)
def test_to_int_exceptions(value):
	if isinstance(value, int):
		with pytest.raises(RuntimeError):
			XFastTrie._to_int(value, max_trie_entry_size)

	elif isinstance(value, bytes):
		with pytest.raises(RuntimeError):
			XFastTrie._to_int(value, max_trie_entry_size)

	else:
		with pytest.raises(RuntimeError):
			XFastTrie._to_int(value, max_trie_entry_size)


@given(valid_trie_entries, valid_int_entries)
def test_get_closest_ancestor(entries, test_values):
	t = XFastTrie(max_trie_entry_size)

	for entry in entries:
		t += entry

	entries = [t._to_int(e, t._maxlen) for e in entries]

	for val in test_values:
		ancestor, level = t._get_closest_ancestor(val)

		if val in entries:
			assert ancestor.leaf
			assert ancestor.value == val

		else:
			test_bits = format(val, 'b').zfill(t._maxlen)[:level + 2]
			assert not ancestor.leaf
			assert not ancestor.left.value_bits.startswith(test_bits)
			assert not ancestor.right.value_bits.startswith(test_bits)


@given(valid_trie_entries, valid_int_entries)
def test_get_closest_leaf(entries, test_values):
	t = XFastTrie(max_trie_entry_size)

	for entry in entries:
		t += entry

	entries = [t._to_int(e, t._maxlen) for e in entries]

	for val in test_values:
		neighbor = t._get_closest_leaf(val)
		assert neighbor.leaf

		if val in entries:
			assert neighbor.value == val

		else:
			if neighbor.pred is not None:
				assert abs(neighbor.value - val) <= abs(neighbor.pred.value - val)

			if neighbor.succ is not None:
				assert abs(neighbor.value - val) <= abs(neighbor.succ.value - val)


@given(valid_trie_entries, valid_int_entries)
def test_predecessor(entries, test_values):
	t = XFastTrie(max_trie_entry_size)

	for entry in entries:
		t += entry

	for val in test_values:
		pred = t < val

		if pred is not None:
			assert pred < val
			pred = t.predecessor(val)

			if pred.succ is not None:
				assert pred.succ.value >= val


@given(valid_trie_entries, valid_int_entries)
def test_successor(entries, test_values):
	t = XFastTrie(max_trie_entry_size)

	for entry in entries:
		t += entry

	for val in test_values:
		succ = t > val

		if succ is not None:
			assert succ > val
			succ = t.successor(val)

			if succ.pred is not None:
				assert succ.pred.value <= val


def test_successor_predecessor_empty_trie():
	t = XFastTrie(max_trie_entry_size)

	with pytest.raises(RuntimeError):
		t.successor(0)

	with pytest.raises(RuntimeError):
		t.predecessor(0)


@given(valid_trie_entries)
def test_clear(entries):
	t = XFastTrie(max_trie_entry_size)

	for entry in entries:
		t += entry

	assert t.count > 0
	assert t.min is not None
	assert t.max is not None

	t.clear()

	for d in t._level_tables:
		assert len(d) == 0

	assert t.count == 0
	assert t.min is None
	assert t.max is None

class XFastStateMachine(RuleBasedStateMachine):
	def __init__(self):
		super(XFastStateMachine, self).__init__()
		self.t = XFastTrie(max_trie_entry_size)

	def teardown(self):
		values = list(self.t._level_tables[-1])

		for val in values:
			self.t -= val

	@invariant()
	def valid_count(self):
		assert self.t.count == len(self.t._level_tables[-1])

	@invariant()
	def valid_min(self):
		if self.t.count > 0:
			assert self.t.min.pred is None

			for leaf in self.t._level_tables[-1].values():
				assert leaf is self.t.min or self.t.min.value < leaf.value

	@invariant()
	def valid_max(self):
		if self.t.count > 0:
			assert self.t.max.succ is None

			for leaf in self.t._level_tables[-1].values():
				assert leaf is self.t.max or self.t.max.value > leaf.value

	@invariant()
	def valid_pointers(self):
		for (level, table) in enumerate(self.t._level_tables):
			for node in table.values():
				if not node.leaf:
					left_child_value = node.value << 1 & -2
					right_child_value = node.value << 1 | 1
					left_child = self.t._level_tables[level + 1].get(left_child_value)
					right_child = self.t._level_tables[level + 1].get(right_child_value)

					# While we're in here, make sure the node should be in the trie
					assert left_child is not None or right_child is not None

					if left_child is not None:
						assert node.left is left_child
						assert left_child.parent is node
					else:
						desc = node.right

						while not desc.leaf:
							desc = desc.left

						assert node.left is desc

					if right_child is not None:
						assert node.right is right_child
						assert right_child.parent is node
					else:
						desc = node.left

						while not desc.leaf:
							desc = desc.right

						assert node.right is desc
				else:
					if node.pred is not None:
						assert node.pred.value < node.value

					if node.succ is not None:
						assert node.succ.value > node.value

	@rule(val=valid_trie_entry)
	def insert_value(self, val):
		self.t += val

	@rule(val=valid_trie_entry)
	def remove_value(self, val):
		if val not in self.t:
			try:
				self.t -= val
			except RuntimeError:
				pass
		else:
			self.t -= val

test_x_fast_trie = XFastStateMachine.TestCase