"""Smoke tests for the keyflux package scaffold."""

import keyflux


class TestPackage:
    """The package imports and exposes its version."""

    def test_importable(self) -> None:
        assert keyflux is not None

    def test_has_version(self) -> None:
        assert isinstance(keyflux.__version__, str)
        assert keyflux.__version__.count(".") == 2
