# RentAll — rental marketplace (university project)

Rent or list cars, bikes, scooters, apartments, event venues.
Course: SU DevOps & Cloud Fundamentals 2026. Weekly live demos, so main must always work.

## Stack
- Python 3.12, Flask 3 (app factory `create_app`, blueprints), SQLAlchemy 2 (Mapped/mapped_column), Flask-Migrate
- PostgreSQL 16 everywhere (Docker locally), no SQLite
- Flask-Login, Flask-WTF (CSRF on), Werkzeug password hashing
- Jinja2 + Bootstrap 5 (CDN), vanilla JS, Leaflet + OpenStreetMap for maps
- Later: Stripe Checkout + webhook, Cloudinary for photos, Flask-Mail
- pytest + pytest-cov, ruff, pre-commit; Docker, docker-compose, GitHub Actions; deploy on Render (gunicorn)

## Structure
app/__init__.py (create_app), app/extensions.py, app/models/, app/services/ (business logic),
app/<blueprint>/{routes.py,forms.py}, app/templates/<blueprint>/, tests/, config.py, wsgi.py

## Rules
- Business logic in app/services/, not in routes. Routes stay thin.
- Secrets only from environment (.env, never committed; keep .env.example updated).
- Every feature comes with pytest tests; `ruff check .` and `pytest` must pass before finishing.
- UI text in Russian, code/comments/commits in English. Conventional Commits (feat:, fix:, test:, docs:, ci:).
- Price units: `hour` or `day`. Price is always computed on the server.
- Bookings must never overlap for active statuses (pending, confirmed, paid).
- Owner-only actions return 403 for other users.
- Do not add features outside the current task. Ask if something is unclear.
