# encoding: utf-8

################################################################################
#                                 py-fast-trie                                 #
#          Python library for tries with different grades of fastness          #
#                            (C) 2020, Jeremy Brown                            #
#       Released under version 3.0 of the Non-Profit Open Source License       #
################################################################################

from os import getenv

import pytest

from hypothesis import example, given, HealthCheck, settings
from hypothesis.strategies import (binary,
								   integers,
								   one_of,
								   )

settings.register_profile(u"ci", database=None, deadline=300, suppress_health_check=[HealthCheck.too_slow])
settings.load_profile(getenv(u"HYPOTHESIS_PROFILE", u"default"))
