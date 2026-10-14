import click
from flask import Flask

from app.services.seed import SEED_PASSWORD, seed


def register_commands(app: Flask) -> None:
    @app.cli.command("seed")
    def seed_command():
        """Load demo categories, users and listings (idempotent)."""
        result = seed()
        click.echo(
            f"Created: {result.categories} categories, {result.users} users, "
            f"{result.listings} listings."
        )
        click.echo(f"Demo users' password: {SEED_PASSWORD}")
