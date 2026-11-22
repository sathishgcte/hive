# Hive — Apartment Maintenance Accounts

A small, server-rendered Python learning project for one apartment complex.

## Included

- Login-protected pages; all authenticated users have the same access.
- Add/edit flats and their default maintenance rate; deactivate rather than delete.
- Generate monthly charges without duplicating a flat/month or changing old amounts.
- Receive full or partial payments against a specific maintenance month.
- Reject zero, negative and excess payments through the application workflow.
- Record expenses by date, category and payment mode.
- Dashboard: receipt-month collections, payment-month expenses, net movement and outstanding maintenance.
- Tests and a GitHub Actions workflow.

## Requirements

Python 3.12 recommended. Django 5.2.x and SQLite. No Node.js or separate database server is needed for this first version.

## Local setup — macOS / Linux

```bash
git clone https://github.com/sathishgcte/hive.git
cd hive
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py makemigrations accounts
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

On Windows use `py -m venv .venv`, then `.venv\Scripts\activate`, and continue with the `python` commands.

Open http://127.0.0.1:8000/ and sign in with the account you created.

The first `makemigrations accounts` command deliberately generates the initial migration as a learning exercise. Commit the resulting `accounts/migrations/` directory before sharing a persistent deployment. Subsequent checkouts containing that migration should run `migrate`, not regenerate the schema. No real resident data, passwords or database file belongs in Git.

## First walkthrough

1. Add A-101 / Ravi / 2000.00 on Flats.
2. On Maintenance select a month, then generate charges.
3. Open Payments and record 1000.00; status becomes Partial.
4. Record the remaining 1000.00; status becomes Paid.
5. Add a cleaning expense and inspect the dashboard for its payment month.
6. Restart the server and verify the records remain.

Creating a charge snapshots the rate. Changing a flat's current rate does not rewrite previous charges. Generating twice is safe. Only active flats receive new charges.

Collections use payment date, not charge month. Outstanding uses the selected charge month and all payments recorded against it. It is a current outstanding figure, not a historical month-end snapshot. No generated charges means no recorded dues; it does not prove that nothing is owed.

## Tests

```bash
python manage.py check
python manage.py test accounts
```

GitHub Actions installs dependencies, generates the initial migration, applies it and runs tests. Workflow results, not this README, establish whether a commit passed.

## Code map and learning order

1. `accounts/models.py`: classes, fields, relationships, Decimal amounts.
2. `accounts/forms.py`: browser inputs and validation.
3. `accounts/services.py`: charge generation and payment rules.
4. `accounts/views.py`: requests, queries, calculations and responses.
5. `hive/urls.py`: map browser URLs to Python functions.
6. `templates/`: HTML, loops, conditions and CSRF-protected forms.
7. `accounts/tests.py`: repeatable examples and edge cases.

Request flow: browser -> URL -> view -> form/service -> model/database -> template -> browser.

## Scope and safety

This is a local learning starter, not production accounting software. Net movement is not bank balance. Opening funds, advances, refunds, reversals, audit trails, receipts, penalties, reconciliation and role-based permissions are not implemented. Payment and expense correction/deletion screens are deliberately absent; do not use real accounts until audited correction workflows exist.

SQLite is intended here for local, low-concurrency learning. `select_for_update` does not provide row locks on SQLite; concurrent writes may fail with database-locked errors. Move to PostgreSQL and test concurrent payment entry before multi-user deployment. The admin ledger tables are read-only to avoid bypassing application payment rules; the Django shell is still privileged access.

The development server binds to localhost by default. Do not expose it publicly. Before deployment set `DJANGO_DEBUG=0`, a private `DJANGO_SECRET_KEY`, and comma-separated `DJANGO_ALLOWED_HOSTS` in the process environment; environment files are not loaded automatically. Add HTTPS, secure cookie settings, a production server, backups, access controls and deployment checks. Keep `.env`, `db.sqlite3` and credentials out of Git.
