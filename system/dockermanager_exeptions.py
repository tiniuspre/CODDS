from __future__ import annotations


class InvalidPinExceptionError(Exception):
    def __init__(self, message: str):
        self.message = message
