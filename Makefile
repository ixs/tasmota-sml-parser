BRANCH := $(shell git branch --show-current)

venv:
	pyenv exec python3 -mvenv venv
	./venv/bin/pip install -r requirements.txt

dev-deploy:
	git push azure-dev $(BRANCH):master

prod-deploy:
	git push azure-prod $(BRANCH):master
