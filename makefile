
pwd = $(shell pwd)
name = dioxus_widget
email = $(shell cat "$$HOME/.secret/email.txt")
version = $(shell yq ".project.version" pyproject.toml)

binlink = ${HOME}/.local/bin/$(name)
srclink = $(pwd)/$(name)
venv = $(pwd)/.venv
venvbin = $(venv)/bin
activate = $(venv)/bin/activate

define clear_dir
    if [ -d $(1) ]; then rm -r $(1); fi
    mkdir $(1)
endef

$(venv): $(venvbin) $(binlink) $(srclink)
	touch $(venv)

$(venvbin): $(activate) requirements.txt
	. .venv/bin/activate && \
	pip install -r requirements.txt
	touch $(venvbin)

$(activate):
	python -m venv --prompt $(name) .venv
	. .venv/bin/activate && \
	pip install --upgrade pip;

$(binlink):
	echo "#!/bin/sh\n$(venv)/bin/python $(pwd)/src/main.py \"\$$@\"" > $(binlink)
	chmod +x $(binlink)

$(srclink):
	ln -s "./src" "$(srclink)"
	sed 's/NAME/$(name)/' pyproject.toml > pyproject.temp
	mv pyproject.temp pyproject.toml
	
# Make sure to have a public branch, possibly by running make share_init
share: $(venv)
	git checkout main && \
	git push public --tags

test_local: $(venv)
	python -m unittest src.tests

build:
	$(call clear_dir,dist)
	mv pyproject.toml pyproject.temp
	sed 's/^email = .*/email = "$(email)"/' pyproject.temp > pyproject.toml
	python -m build
	mv pyproject.temp pyproject.toml

increment_patch:
	$(eval patch = $(shell echo $(version) | grep -o '[0-9]*$$'))
	$(eval patch = $(shell echo "$$(($(patch)+1))"))
	$(eval majorminor = $(shell echo $(version) | grep -o '^[0-9]*.[0-9]*.'))
	$(eval version = $(majorminor)$(patch))
	sed 's/version = .*/version = "$(version)"/' pyproject.toml > pyproject.temp
	mv pyproject.temp pyproject.toml
	echo "$(version)"

test: $(venv) test_local increment_patch build
	twine upload dist/* -r pypitest
	$(call clear_dir,"tmp")
	cd tmp && \
	python -m venv .venv
	. tmp/.venv/bin/activate && \
	pip install --extra-index-url "https://test.pypi.org/simple" "$(name) == $(version)" || \
	pip install --extra-index-url "https://test.pypi.org/simple" "$(name) == $(version)" && \
	python -m unittest "$(name).tests"

publish: $(venv)
	$(call clear_dir,"dist")
	python -m build
	twine upload dist/*

to_github:
	$(eval user_name = $(shell yq ".git.github" pyproject.toml))
	curl -u "$(user_name)" "https://api.github.com/user/repos" -d "{\"name\":\"$(name)\",\"private\":false}"

share_init:
	git checkout -b main || git checkout main
	$(eval user_name = $(shell yq ".git.github" pyproject.toml))
	git remote add github "https://github.com/$(user_name)/$(name)"
	git remote add public "/mnt/nas/git/$(name)"
	git remote set-url --add --push public "/mnt/nas/git/$(name)"
	git remote set-url --add --push public "https://github.com/$(user_name)/$(name)"
	git push public main

clean:
	rm -r .venv
	rm $(binlink)
	rm $(srclink)

