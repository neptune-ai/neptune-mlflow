clean:
	rm -fr .tox/ dist/ VERSION

prepare:
	pip install -r requirements.txt -r test_requirements.txt

build:
	python setup.py git_version sdist

tests: unit_tests

unit_tests:
	tox
