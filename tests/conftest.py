import pytest

from verify_web import read_config


@pytest.fixture(scope="session")
def harbor():
    try:
        return read_config()
    except ValueError as error:
        pytest.fail(str(error))
