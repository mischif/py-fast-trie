################################################################################
#                                 py-fast-trie                                 #
#          Python library for tries with different grades of fastness          #
#                            (C) 2020, Jeremy Brown                            #
#       Released under version 3.0 of the Non-Profit Open Source License       #
################################################################################

CI_OPTIONS="--cov-report xml"

.PHONY: test ci-test build

clean:
	rm -rf .coverage coverage.xml .eggs/ .hypothesis/ .pytest_cache/ *egg-info/ dist/ build/
	find . -name __pycache__ -exec rm -rf {} +
	find . -name *.pyc -exec rm -rf {} +

test:
	python -B setup.py test

ci-test:
	HYPOTHESIS_PROFILE=ci python setup.py test --addopts ${CI_OPTIONS}

build:
	python setup.py build sdist bdist_wheel
