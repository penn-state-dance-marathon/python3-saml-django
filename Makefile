coverage:
	coverage run django_test/manage.py test tests
	coverage report

validate:
	isort . -rc -c
	flake8 . --count

check:
	python manage.py check

all: validate check coverage
