test:
	pip install -r tests/requirements.txt
	coverage run -m unittest discover tests
