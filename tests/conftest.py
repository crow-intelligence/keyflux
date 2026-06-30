"""Shared pytest fixtures for keyflux tests."""

import os
from collections import Counter

import pytest
from hypothesis import HealthCheck, settings

# Mutation testing (mutmut) runs the same property test from multiple forked
# workers, which trips Hypothesis's ``differing_executors`` health check. This
# env-gated profile suppresses that check (and the shared example database) only
# during mutation runs — the normal test suite is unaffected.
settings.register_profile(
    "mutation",
    suppress_health_check=[HealthCheck.differing_executors],
    database=None,
    deadline=None,
)
if os.environ.get("KEYFLUX_MUTATION"):
    settings.load_profile("mutation")


@pytest.fixture
def tiny_focus() -> Counter[str]:
    """A small focus-corpus frequency table."""
    return Counter({"climate": 30, "carbon": 12, "the": 80, "policy": 9, "and": 40})


@pytest.fixture
def tiny_reference() -> Counter[str]:
    """A small reference-corpus frequency table."""
    return Counter({"climate": 3, "carbon": 1, "the": 78, "market": 15, "and": 42})
