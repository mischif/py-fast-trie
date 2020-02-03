# encoding: utf-8

################################################################################
#                                 py-fast-trie                                 #
#          Python library for tries with different grades of fastness          #
#                            (C) 2020, Jeremy Brown                            #
#       Released under version 3.0 of the Non-Profit Open Source License       #
################################################################################

from hypothesis import HealthCheck, settings
from hypothesis.database import ExampleDatabase

settings.register_profile(u"ci",
						  database=ExampleDatabase(":memory:"),
						  deadline=None,
						  max_examples=500,
						  stateful_step_count=200,
						  suppress_health_check=[HealthCheck.too_slow])
