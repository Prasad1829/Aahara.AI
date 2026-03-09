.PHONY: run test migrate format

run:
	cd backend && python run.py

test:
	cd backend && pytest --cov=app tests/

migrate:
	cd backend && flask --app run.py db upgrade

format:
	cd backend && black .
