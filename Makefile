################################################################################
#                                 py-fast-trie                                 #
#          Python library for tries with different grades of fastness          #
#                            (C) 2020, Jeremy Brown                            #
#       Released under version 3.0 of the Non-Profit Open Source License       #
################################################################################

.POSIX:

.PHONY: ci-test clean release test

clean:
	rm -rf .coverage coverage.xml .eggs/ .hypothesis/ .pytest_cache/ *egg-info/ dist/ build/
	find . -name __pycache__ -exec rm -rf {} +
	find . -name *.pyc -exec rm -rf {} +

test:
	pytest

ci-test:
	pytest --cov-report xml --hypothesis-profile ci

release:
	python -m pep517.build -sb .
