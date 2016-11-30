requirements:
	pip install -r requirements.txt

test:
	python -m unittest -v

coverage:
	coverage run -m unittest && \
	coverage html &&            \
	coverage report

docs:
	(cd docs; make html)

install:
	python setup.py install

dev_install:
	pip install --editable .

dist:
	python setup.py sdist

.PHONY: requirements test coverage docs install dev_install dist
