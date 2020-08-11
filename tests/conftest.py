import pytest

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
    # Insert user data
    # user1 = User(email='patkennedy79@gmail.com', password='FlaskIsAwesome')
    # user2 = User(email='kennedyfamilyrecipes@gmail.com', password='PaSsWoRd')
    # db.session.add(user1)
    # db.session.add(user2)

    yield db

    db.session.remove()
    db.drop_all()
