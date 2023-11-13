.PHONY: all install list release test version


VERSION := '0.0.0'


all: list

install:
	pip install -r requirements.test.txt


list:
	@grep '^\.PHONY' Makefile | cut -d' ' -f2- | tr ' ' '\n'

release:
	bash -c '[[ -z `git status -s` ]]'
	git tag -a -m release $(VERSION)
	git push --tags

test:
	pylama 
	py.test

version:
	@echo $(VERSION)
