.PHONY: build ddraft

build:
	docker compose build --no-cache

ddraft:
	docker compose run --rm --service-ports dialogue-draft bash
