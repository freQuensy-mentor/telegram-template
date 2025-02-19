.PHONY: run lint build

run:
	docker compose up --build

build:
	docker compose build

lint:
	docker compose run --rm bot black .

stop:
	docker compose down

logs:
	docker compose logs -f

shell:
	docker compose run --rm bot bash 