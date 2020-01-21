# encoding: utf-8

################################################################################
#                                 py-fast-trie                                 #
#          Python library for tries with different grades of fastness          #
#                            (C) 2020, Jeremy Brown                            #
#       Released under version 3.0 of the Non-Profit Open Source License       #
################################################################################

from functools import partial
from os import getenv
from sys import maxsize

from hypothesis import HealthCheck, settings
from hypothesis.strategies import (binary,
								   integers,
								   lists,
								   none,
								   one_of,
								   )

from py_fast_trie import XFastTrie

settings.register_profile(u"ci", database=None, deadline=300, suppress_health_check=[HealthCheck.too_slow])
settings.load_profile(getenv(u"HYPOTHESIS_PROFILE", u"default"))

to_int = partial(XFastTrie._to_int, length=(maxsize.bit_length() + 1))

max_trie_size = maxsize if getenv(u"HYPOTHESIS_PROFILE", u"default") == "ci" else 2 ** 24

invalid_binary_entry = binary(min_size=((maxsize.bit_length() + 9) / 8))
invalid_int_entry = one_of(integers(max_value=-1),
						   integers(min_value=(2 ** (maxsize.bit_length() + 1))))
invalid_trie_entry = one_of(invalid_binary_entry, invalid_int_entry, none())

valid_binary_entry = binary(min_size=1, max_size=((maxsize.bit_length() + 1) / 8))
valid_int_entry = integers(min_value=0, max_value=maxsize)
valid_int_entries = lists(valid_int_entry, min_size=1, max_size=max_trie_size, unique_by=to_int)
valid_trie_entry = one_of(valid_binary_entry, valid_int_entry)
valid_trie_entries = lists(valid_trie_entry, min_size=1, max_size=max_trie_size, unique_by=to_int)
