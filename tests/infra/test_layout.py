import pytest


def test_nginx_can_parse_config(host):
    check = host.run("nginx -t")
    assert check.rc == 0, check.stderr


@pytest.mark.parametrize(
    "filename",
    [
        "/etc/nginx/conf.d/default.conf",
        "/usr/share/nginx/html/index.html",
        "/usr/share/nginx/html/health.json",
    ],
    ids=["server-config", "landing-page", "health-metadata"],
)
def test_expected_file_exists(host, filename):
    assert host.file(filename).is_file, f"Required file missing: {filename}"


def test_local_index_identifies_release(host, harbor):
    assert host.file("/usr/share/nginx/html/index.html").contains(harbor.release)
