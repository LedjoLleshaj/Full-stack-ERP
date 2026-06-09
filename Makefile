.PHONY: up down build test lint migrate shell

up:
	docker compose up --build -d

down:
	docker compose down

build:
	docker compose build

test:
	cd backend && .venv/bin/pytest -v

lint:
	cd backend && .venv/bin/ruff check erp/

migrate:
	cd backend && .venv/bin/python manage.py migrate

shell:
	cd backend && .venv/bin/python manage.py shell

seed:
	docker compose exec -T db psql -U postgres -d erp_db < db/seed.sql

clean:
	docker compose down -v
