.PHONY: all install list release test version


VERSION := '0.0.0'


all: list

install:
	pip install --upgrade -e .[develop]

list:
	@grep '^\.PHONY' Makefile | cut -d' ' -f2- | tr ' ' '\n'

lint:

release:
	bash -c '[[ -z `git status -s` ]]'
	git tag -a -m release $(VERSION)
	git push --tags

test:
	pip install -r requirements.test.txt
	pylama 
	py.test

version:
	@echo $(VERSION)
