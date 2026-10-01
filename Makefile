.PHONY: register unregister

register:
	cca register cca-scrapi --issue $(filter-out $@,$(MAKECMDGOALS))

unregister:
	cca unregister cca-scrapi --issue $(filter-out $@,$(MAKECMDGOALS))

%:
	@:
