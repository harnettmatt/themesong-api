# All
start:
	docker-compose up -d

rebuild:
	docker-compose up --build --force-recreate --detach

stop:
	docker-compose down

delete:
	docker-compose down --volumes

docs:
	open http://127.0.0.1:8000/docs

# Local
start-local: db-start
	pipenv run uvicorn app.main:app --reload

# DB
db-start:
	docker-compose up -d db

db-connect:
	docker exec -it themesong-db-1 bash

# Dev Tools
lint:
	pre-commit run --all-files

unit-tests:
	pipenv run pytest -m "not integtest"

int-tests: db-start-detach
	pipenv run pytest -m "integtest"
