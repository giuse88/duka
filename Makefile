test-register:
	python setup.py register -r pypitest

test-release: test-register
	python setup.py sdist upload -r pypitest

register:
	python setup.py register -r pypi

release: register
	python setup.py sdist upload -r pypi
