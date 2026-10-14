# RentAll

**Status: Week 1 — Planning**

RentAll is an all-in-one rental marketplace where people can rent or list cars, bikes, scooters, apartments and event venues. Owners publish listings with hourly or daily prices. Renters search the catalog on a map, book available dates, pay online and leave reviews. The platform guarantees that active bookings never overlap.

University project for the SU DevOps & Cloud Fundamentals 2026 course.

## Tech stack

- **Backend:** Python 3.12, Flask 3 (app factory, blueprints), SQLAlchemy 2, Flask-Migrate
- **Database:** PostgreSQL 16 (Docker locally)
- **Auth & security:** Flask-Login, Flask-WTF (CSRF), Werkzeug password hashing
- **Frontend:** Jinja2, Bootstrap 5, vanilla JS, Leaflet + OpenStreetMap
- **Integrations (planned):** Stripe Checkout + webhooks, Cloudinary (photos), Flask-Mail
- **Quality:** pytest + pytest-cov, ruff, pre-commit
- **DevOps:** Docker, docker-compose, GitHub Actions CI/CD, deployment on Render (gunicorn)

## Planned features

- User registration and login
- Owner role: create, edit and hide listings with photos and a map location
- Catalog with search, filters, sorting and a map view
- Listing details page with an availability calendar
- Bookings with hourly or daily pricing calculated on the server
- Protection against overlapping bookings (pending, confirmed, paid)
- Owner confirms or declines booking requests
- Online payment with Stripe Checkout
- Email notifications on booking status changes
- Reviews and ratings after a completed rental
- User dashboard for bookings, listings and incoming requests

## Documentation

- [User flows](docs/user-flows.md)
- [Key pages](docs/pages.md)
- [Competitor analysis](docs/competitors.md)
