# All
start: db-start-detach app-start

get-groups:
	curl http://127.0.0.1:8000/groups | jq

docs:
	open http://127.0.0.1:8000/docs

# App
app-start:
	pipenv run uvicorn main:APP --reload

# DB
db-start:
	docker-compose up

db-start-detach:
	docker-compose up --detach

db-connect:
	docker exec -it rankings-db-1 bash

# Dev Tools
lint:
	pre-commit run --all-files

unit-tests:
	pipenv run pytest -m "not integtest"

int-tests: db-start-detach
	pipenv run pytest -m "integtest"
