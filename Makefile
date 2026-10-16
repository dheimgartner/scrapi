.PHONY: register unregister webpage

register:
	cca register cca-scrapi --issue $(filter-out $@,$(MAKECMDGOALS))

unregister:
	cca unregister cca-scrapi --issue $(filter-out $@,$(MAKECMDGOALS))

webpage:
	uv run mkdocs gh-deploy

%:
	@:
