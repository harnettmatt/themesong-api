# Environment variables for project
include .env
export

# All
start:
	docker compose up

watch:
	docker compose up --build --force-recreate --watch

rebuild:
	docker compose up --build --force-recreate --detach

public:
	ngrok http http://127.0.0.1:8000

docs:
	open http://127.0.0.1:8000/docs

# DB
db-start:
	docker compose up -d db

db-connect:
	docker exec -it themesong-db bash

tail:
	docker container logs -f themesong-api

tail-db:
	docker container logs -f themesong-db

# Dev Tools
lint:
	pre-commit run --all-files

unit-tests:
	pipenv run pytest -m "not integtest"

int-tests: db-start-detach
	pipenv run pytest -m "integtest"

# strava
create-strava-subscription:
	curl -X POST https://www.strava.com/api/v3/push_subscriptions \
      -F client_id=${STRAVA_CLIENT_ID} \
      -F client_secret=${STRAVA_CLIENT_SECRET} \
      -F callback_url=${HOST}/strava/webhook \
      -F verify_token=${STRAVA_WEBHOOK_TOKEN}

view-strava-subscription:
	curl -G https://www.strava.com/api/v3/push_subscriptions \
		-d client_id=${STRAVA_CLIENT_ID} \
		-d client_secret=${STRAVA_CLIENT_SECRET}

# TODO: need to fetch the subscription id from the view-strava-subscription command and use it in this command
delete-strava-subscription:
	curl -X DELETE "https://www.strava.com/api/v3/push_subscriptions/268519?client_id=${STRAVA_CLIENT_ID}&client_secret=${STRAVA_CLIENT_SECRET}"

