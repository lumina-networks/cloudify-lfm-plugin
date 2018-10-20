.PHONY: release install clean source_package source_deploy files test docs prepare publish wagon delete upload

all:
	@echo "make release - prepares a release and publishes it"
	@echo "make dev - prepares a development environment"
	@echo "make package - package for deployment"
	@echo "make deploy - package and deploy with parameters user host and port"
	@echo "make install - install on local system"
	@echo "make files - update changelog and todo files"
	@echo "make test - run tox"
	@echo "make docs - build docs"
	# @echo "make publish - upload to pypi"
	@echo "make wagon - make wagon for upload to Cloudify"

release: test docs publish

dev:
	pip install -r dev-requirements.txt
	python setup.py develop

install:
	python setup.py install

clean:
	rm -f cloudify-lfm-plugin.tar.gz; find . -type f -name '.DS_Store' -delete

source_package:
	make clean; tar -zcvf ../cloudify-lfm-plugin.tar.gz --exclude='__MACOSX' --exclude='*.DS_Store'  --exclude='*.pyc' --exclude='.idea' --exclude='.git' --exclude='.env' --exclude='.venv' --exclude='*.tar.gz' -C .. ./cloudify-lfm-plugin

source_deploy:
	make source_package && \
	cat ../cloudify-lfm-plugin.tar.gz | ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no $(user)@$(host) -p $(port) \
	"tar -zxvf - -C $(path)"

package:
	make source_package;

deploy:
	source_deploy;

files:
	grep '# TODO' -rn * --exclude-dir=docs --exclude-dir=build --exclude=TODO.md | sed 's/: \+#/:    # /g;s/:#/:    # /g' | sed -e 's/^/- /' | grep -v Makefile > TODO.md
	git log --oneline --decorate --color > CHANGELOG

test:
	pip install tox
	tox

docs:
	pip install sphinx sphinx-rtd-theme
	cd docs && make html
	pandoc README.md -f markdown -t rst -s -o README.rst

replace:
	make dev
	make wagon
	make delete
	make upload

delete: 
	cfy plugin list | grep cloudify-lfm-plugin | awk {'print $$2'} | xargs cfy plugin delete

upload:
	cfy plugin upload -y plugin.yaml cloudify_lfm_plugin-*.wgn

wagon:
	wagon create -r dev-requirements.txt -f .
	#wagon create -f -r -s .
