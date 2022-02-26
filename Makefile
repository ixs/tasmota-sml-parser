BRANCH := $(shell git branch --show-current)

dev-deploy:
	git push azure-dev $(BRANCH):master

prod-deploy:
	git push azure-prod $(BRANCH):master
