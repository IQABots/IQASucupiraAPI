import pytest

from iqa.nlp.nlu import NLU
from api.server import app
from api.server.settings import db

@pytest.fixture(scope="module")
def client():
    app.config.from_object("api.server.config.TestingConfig")
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


@pytest.fixture
def dev_app():
    app.config.from_object("api.server.config.DevelopmentConfig")
    yield app
    app.config.from_object("api.server.config.TestingConfig")


@pytest.fixture
def prod_app():
    app.config.from_object("api.server.config.ProductionConfig")
    yield app
    app.config.from_object("api.server.config.TestingConfig")


@pytest.fixture()
def init_db():
    db.create_all()
    db.session.commit()
    yield db

    db.session.remove()
    db.drop_all()


@pytest.fixture(scope="module")
def nlu_obj():
    return NLU()
