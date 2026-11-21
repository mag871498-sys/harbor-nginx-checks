import pytest
import requests


@pytest.fixture
def fetch(harbor):
    def get(path):
        return requests.get(
            harbor.base_url + path,
            timeout=harbor.seconds,
            allow_redirects=False,
        )

    return get


@pytest.mark.parametrize(
    ("path", "code"),
    [("/", 200), ("/health.json", 200), ("/missing-page", 404)],
    ids=["landing", "health", "missing"],
)
def test_response_code(fetch, path, code):
    assert fetch(path).status_code == code


def test_landing_marker(fetch, harbor):
    response = fetch("/")
    assert response.status_code == 200
    assert harbor.release in response.text


def test_health_fields(fetch, harbor):
    response = fetch("/health.json")
    assert response.status_code == 200
    assert response.headers["Content-Type"].split(";")[0] == "application/json"
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        pytest.fail("health.json returned HTTP 200 but contains invalid JSON")
    assert isinstance(data, dict)
    assert data.get("status") == "ready"
    assert data.get("release") == harbor.release
