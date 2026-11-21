from subprocess import CompletedProcess, TimeoutExpired

import pytest

import verify_web


@pytest.fixture
def test_env(monkeypatch):
    monkeypatch.setenv("BASE_URL", "http://harbor.invalid:9123/")
    monkeypatch.setenv("EXPECTED_RELEASE", "test-harbor")
    monkeypatch.setenv("CHECK_TIMEOUT", "1.5")


def test_command_uses_environment(test_env, monkeypatch, capsys):
    def completed(args, *, capture_output, text, timeout):
        assert args == ["curl", "-q", "-fsS", "--", "http://harbor.invalid:9123/"]
        assert capture_output and text and timeout == 1.5
        return CompletedProcess(args, 0, "<strong>test-harbor</strong>", "")

    monkeypatch.setattr(verify_web.subprocess, "run", completed)
    assert verify_web.main() == 0
    assert capsys.readouterr().out == "PASS | test-harbor found at http://harbor.invalid:9123/\n"


@pytest.mark.parametrize(
    ("code", "body", "message"),
    [(22, "", "FAIL curl (22)"), (0, "foreign-release", "FAIL release")],
)
def test_failed_verification(test_env, monkeypatch, capsys, code, body, message):
    def completed(args, **kwargs):
        return CompletedProcess(args, code, body, "request failed")

    monkeypatch.setattr(verify_web.subprocess, "run", completed)
    assert verify_web.main() == 1
    assert message in capsys.readouterr().out


def test_subprocess_timeout(test_env, monkeypatch, capsys):
    def stalled(args, **kwargs):
        raise TimeoutExpired(args, kwargs["timeout"])

    monkeypatch.setattr(verify_web.subprocess, "run", stalled)
    assert verify_web.main() == 2
    assert "exceeded 1.5s" in capsys.readouterr().out


def test_invalid_timeout(test_env, monkeypatch, capsys):
    def must_not_run(*args, **kwargs):
        pytest.fail("Invalid configuration reached curl")

    monkeypatch.setenv("CHECK_TIMEOUT", "0")
    monkeypatch.setattr(verify_web.subprocess, "run", must_not_run)
    assert verify_web.main() == 1
    assert "FAIL configuration" in capsys.readouterr().out
