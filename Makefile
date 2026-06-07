.PHONY: up down build test lint migrate shell

up:
	docker compose up --build -d

down:
	docker compose down

build:
	docker compose build

test:
	cd backend && source .venv/bin/activate && pytest -v

lint:
	cd backend && source .venv/bin/activate && ruff check erp/

migrate:
	cd backend && source .venv/bin/activate && python manage.py migrate

shell:
	cd backend && source .venv/bin/activate && python manage.py shell

seed:
	docker compose exec -T db psql -U postgres -d erp_db < db/seed.sql

clean:
	docker compose down -v
