"""Scaffold verification test — delete when first real test is written."""


def test_platform_version() -> None:
    """Verify the platform package imports correctly."""
    from anif_platform import __version__

    assert __version__ == "0.1.0"
