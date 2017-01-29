requirements:
	python -m pip install -r requirements.txt

# devo requirements will support documentation, coverage, etc.
devo_requirements:
	python -m pip install -r devo-requirements.txt

test:
	python -m unittest -v

coverage:
	coverage run -m unittest && \
	coverage html &&            \
	coverage report

docs:
	(cd docs; make html)

devo_install:
	python -m pip install --editable .

dist:
	python -m setup sdist bdist_wheel

.PHONY: test coverage docs dist
.PHONY: devo_install
.PHONY: devo_requirements requirements
