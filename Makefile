SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

targets: help

up:
	docker compose up -d --build api

# down command also remove postgresql volume 
down:
	docker compose down
	docker volume rm mergify-stargazers_postgres-data

done: check test ## Prepare for a commit
test: utest itest  ## Run unit and integration tests

ci-compose := docker compose -f .ci/docker-compose.yml

utest: cleantest ## Run unit tests
	$(ci-compose) run --rm unit pytest -m unit .

itest: cleantest ## Run integration tests
	$(ci-compose) run --rm integration pytest -sm integration .

check: cleantest ## Check the code base
	$(ci-compose) run --rm unit pre-commit run -a

cleantest:  ## Clean up test containers
	$(ci-compose) kill
	$(ci-compose) down --remove-orphans
	$(ci-compose) build


## Migrations

migrations: ## Generate a migration using alembic
ifeq ($(m),)
	@echo "Specify a message with m={message} and a rev-id with revid={revid} (e.g. 0001 etc.)"; exit 1
else ifeq ($(revid),)
	@echo "Specify a message with m={message} and a rev-id with revid={revid} (e.g. 0001 etc.)"; exit 1
else
	docker compose run api alembic revision --autogenerate -m "$(m)" --rev-id="$(revid)"
endif

migrate: ## Run migrations upgrade using alembic
	docker compose run --rm api alembic upgrade head

downgrade: ## Run migrations downgrade using alembic
	docker compose run --rm api alembic downgrade -1

help: ## Display this help message
	@awk -F '##' '/^[a-z_]+:[a-z ]+##/ { print "\033[34m"$$1"\033[0m" "\n" $$2 }' Makefile
