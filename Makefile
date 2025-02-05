system/setup/Makefile
Makefile

.PHONY: install build test clean

install:
	pip install -r requirements.txt

build:
	python setup.py sdist bdist_wheel

test:
	python -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf build dist __pycache__ *.egg-info
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

