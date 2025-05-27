STORAGES = docker/dev.storages.yaml
ENV = --env-file .env

.PHONE: pre-commit
pre-commit:
	pre-commit install

.PHONY: storages
storages:
	docker compose -f ${STORAGES} ${ENV} -p console-storages up -d --remove-orphans

.PHONY: storages-logs
storages-logs:
	docker compose -f ${STORAGES} ${ENV} -p console-storages up  --remove-orphans

.PHONY: storages-down
storages-down:
	docker compose -f ${STORAGES} ${ENV} -p console-storages down

.PHONY: migrations
migrations:
	python manage.py makemigrations
	python manage.py migrate

.PHONY: app
app:
	python manage.py runserver

.PHONY: shell
shell:
	python manage.py shell

.PHONE: lint
lint:
	isort .
	black . --line-length=120 --target-version=py312
