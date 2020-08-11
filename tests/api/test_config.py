import pytest
import os

from flask import current_app
from api.server import app


postgres_connection_uri = os.getenv("DB_URL")

def test_app_is_development(dev_app):
    assert app.config["SECRET_KEY"] is not "secret-key"
    assert app.config["DEBUG"] is True
    assert current_app is not None
    assert (
        app.config["SQLALCHEMY_DATABASE_URI"]
        == postgres_connection_uri
    )


def test_app_is_testing():
    assert app.config["SECRET_KEY"] is not "secret-key"
    assert app.config["DEBUG"]
    assert (
        app.config["SQLALCHEMY_DATABASE_URI"]
        == postgres_connection_uri + "_test"
    )

def test_app_is_production(prod_app):
    assert app.config["DEBUG"] is False
