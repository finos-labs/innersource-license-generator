import pytest
from src.flask_app import app


@pytest.fixture()
def test_client():
    app.config.update({
        "TESTING": True,
    })

    with app.test_client() as testing_client:
        # Establish an application context
        with app.app_context():
            yield testing_client  # this is where the testing happens!

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()