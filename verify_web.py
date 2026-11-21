import os
import subprocess
from math import isfinite
from typing import NamedTuple
from urllib.parse import urlsplit


class SiteConfig(NamedTuple):
    base_url: str
    release: str
    seconds: float


def read_config():
    address = os.getenv("BASE_URL", "").strip().rstrip("/")
    release = os.getenv("EXPECTED_RELEASE", "").strip()
    parsed = urlsplit(address)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("BASE_URL must be an HTTP(S) address")
    if not release:
        raise ValueError("EXPECTED_RELEASE is missing")
    seconds = float(os.getenv("CHECK_TIMEOUT", "3"))
    if not isfinite(seconds) or seconds <= 0:
        raise ValueError("CHECK_TIMEOUT must be positive and finite")
    return SiteConfig(address, release, seconds)


def main():
    try:
        config = read_config()
    except ValueError as error:
        print(f"FAIL configuration | {error}")
        return 1

    target = config.base_url + "/"
    command = ["curl", "-q", "-fsS", "--", target]
    try:
        output = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=config.seconds,
        )
    except subprocess.TimeoutExpired:
        print(f"TIME LIMIT | {target} exceeded {config.seconds:g}s")
        return 2
    except OSError as error:
        print(f"FAIL curl | {error}")
        return 1

    if output.returncode:
        print(f"FAIL curl ({output.returncode}) | {output.stderr.strip()}")
        return 1
    if config.release not in output.stdout:
        print(f"FAIL release | expected {config.release} in {target}")
        return 1

    print(f"PASS | {config.release} found at {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
