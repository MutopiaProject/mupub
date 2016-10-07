requirements:
	pip install -r requirements.txt

test:
	python -m unittest

coverage:
	coverage run -m unittest && \
	coverage html &&            \
	coverage report

docs:
	(cd docs; make html)

install:
	python setup.py install

dist:
	python setup.py sdist

.PHONY: requirements test coverage docs dist
