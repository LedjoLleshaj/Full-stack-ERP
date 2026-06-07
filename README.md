# Full-Stack ERP

A multi-currency ERP for small wholesale/retail businesses — inventory, sales, purchasing, clients/suppliers, a cash & bank ledger with partial and cross-currency payments, and live reporting dashboards. Built as a production-shaped Django + Angular monorepo that runs end-to-end with a single `docker compose up`.

<p>
  <img alt="Backend" src="https://img.shields.io/badge/backend-Django%205.1%20%2B%20DRF-092E20">
  <img alt="Frontend" src="https://img.shields.io/badge/frontend-Angular%2016-DD0031">
  <img alt="Database" src="https://img.shields.io/badge/db-PostgreSQL-336791">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
  <img alt="CI" src="https://github.com/ledjolleshaj/Full-stack-ERP/actions/workflows/ci.yml/badge.svg">
</p>

> Why it exists: built to run a real multi-currency (EUR / USD / LEK) trading business where invoices are paid in installments and in whichever currency the customer has on hand — the accounting has to stay correct anyway.

## Screenshots

| Dashboard | Sale detail — cross-currency payment |
|---|---|
| ![Dashboard](docs/screenshots/dashboard.png) | ![Sale detail](docs/screenshots/sale-detail-multicurrency.png) |

<details><summary>More screenshots</summary>

![Login](docs/screenshots/login.png)
![Sales](docs/screenshots/sales.png)
![Inventory](docs/screenshots/inventory.png)

</details>

## Architecture

```mermaid
flowchart LR
    User([User]) -->|HTTPS| NG[Angular 16 SPA<br/>Material · Tailwind · ECharts]
    NG -->|/api · HttpOnly JWT cookie| NGINX[nginx]
    NGINX -->|reverse proxy| API[Django 5.1 + DRF<br/>cookie JWT auth]
    API -->|psycopg2| DB[(PostgreSQL)]
    API -.->|weekly sync| FX[(ExchangeRate-API)]
    subgraph Docker Compose
        NG
        NGINX
        API
        DB
    end
```

**Request flow:** the SPA calls the API with an `HttpOnly`, `SameSite` JWT cookie (no token in JS). DRF authenticates via a cookie-aware `JWTAuthentication`. Exchange rates are fetched from an external API and cached in Postgres, refreshed weekly.

See the full entity-relationship diagram: [`db/ERdatabaseSchema.svg`](db/ERdatabaseSchema.svg).

## Tech stack

| Layer | Tech |
|---|---|
| Frontend | Angular 16, Angular Material, TailwindCSS, ngx-echarts, xlsx |
| Backend | Django 5.1, Django REST Framework, SimpleJWT (cookie-based), gunicorn |
| Database | PostgreSQL |
| Infra | Docker Compose, nginx |
| Quality | pytest, ruff, GitHub Actions, drf-spectacular (OpenAPI) |

## Quickstart

Requires Docker + Docker Compose.

```bash
git clone https://github.com/LedjoLleshaj/Full-stack-ERP.git
cd Full-stack-ERP

# Configure backend env (generates secrets locally; never commit .env)
cp backend/.env.example backend/.env
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(64))"   # paste into backend/.env

docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:4200 |
| API | http://localhost:8080/erp |
| API health | http://localhost:8080/erp/health/ |
| Django admin | http://localhost:8080/admin |

Migrations run automatically on backend startup; a demo admin (`admin` / `adminpass`) is seeded by [`backend/entrypoint.sh`](backend/entrypoint.sh) — change these before any non-local use.

## Project structure

```
.
├── backend/          # Django + DRF API
│   └── erp/          # domain app: models, api/, services/, tests/
├── frontend/         # Angular SPA
├── db/               # schema, ER diagram, seed data
├── docs/             # screenshots
├── scripts/          # deploy / backup / analytics helpers
└── docker-compose.yml
```

## Data model & key decisions

The domain is 13 models. The interesting choices (and their trade-offs):

- **Transaction ↔ Payment ledger.** A `Transaction` (PURCHASE or SALE) carries a total; one or more `Payment` rows settle it. Status (`PENDING` → `PARTIAL` → `COMPLETED`) is derived from payments vs. total. This is what makes **installment payments** first-class instead of a boolean `is_paid`.
- **Cross-currency settlement.** A sale in EUR can be paid in LEK: the `Payment` stores both the converted amount (transaction currency) and the `original_amount`/`original_currency`/`exchange_rate` used. Rates come from a cached `ExchangeRate` table synced weekly.
- **Account ledger.** Every payment moves money in/out of a cash or bank `Account` via an `AccountTransaction` row that records `balance_after`, giving an auditable running balance per account.
- **Soft deletes.** Clients, suppliers, and products use `is_active` flags rather than row deletion, preserving historical transactions.
- **Decimal money.** All monetary values are `DECIMAL` (never float) to avoid rounding errors in accounting.
- **Cookie-based JWT.** Access/refresh tokens live in `HttpOnly` `SameSite` cookies (XSS-resistant) rather than `localStorage`; the trade-off is CSRF surface, mitigated by `SameSite` and same-origin proxying.

## Testing

```bash
# Backend
cd backend && pytest            # or: python manage.py test erp

# Frontend
cd frontend && npm test
```

## License

[MIT](LICENSE)
