requirements:
	python3 -m pip install -r requirements.txt

devo_requirements:
	python3 -m pip install -r requirements.txt
	python3 -m pip install -r devo-requirements.txt

test:
	python -m unittest -v

coverage:
	coverage run -m unittest && \
	coverage html &&            \
	coverage report

docs:
	(cd docs; make html)

install:
	python3 -m pip install -r requirements.txt --user
	python3 -m setup install --user

dev_install:
	python3 -m pip install --editable .

dist:
	python setup.py sdist

.PHONY: test coverage docs dist
.PHONY: install dev_install
.PHONY: devo_requirements requirements
