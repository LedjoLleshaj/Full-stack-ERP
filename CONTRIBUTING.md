# Contributing

## Local Setup

### Backend (Django)

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Server runs at `localhost:8000`.

### Frontend (Angular)

```bash
cd frontend
npm install
npm start
```

App runs at `localhost:4200`.

## Running Tests

### Backend

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm test
```

## Linting

```bash
ruff check backend/
```

Fix auto-fixable issues:

```bash
ruff check --fix backend/
```

## Branch Naming

Use prefixed branch names:

- `feat/short-description` -- new features
- `fix/short-description` -- bug fixes
- `chore/short-description` -- maintenance, deps, config

## Commit Style

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add invoice export endpoint
fix: correct tax calculation rounding
chore: bump Angular to v18
docs: update API examples
refactor: extract shared validation logic
test: add coverage for order service
```

## Pull Request Checklist

Before opening a PR, confirm:

- [ ] All backend tests pass (`pytest`)
- [ ] All frontend tests pass (`npm test`)
- [ ] `ruff check backend/` reports no issues
- [ ] Acceptance checks pass
- [ ] Branch is up to date with `main`
- [ ] Commit messages follow Conventional Commits
