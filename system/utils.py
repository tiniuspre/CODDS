from __future__ import annotations

import hashlib


def md5(data: str) -> str:
    return hashlib.md5(data.encode()).hexdigest()  # noqa
