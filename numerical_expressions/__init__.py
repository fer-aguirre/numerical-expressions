"""Suggest clear, accurate ways to write about numbers in news stories."""

from .describe import DEFAULT_OPERATIONS, OPERATIONS, describe, describe_all
from .results import Options, Result

__all__ = ["DEFAULT_OPERATIONS", "OPERATIONS", "Options", "Result", "describe", "describe_all"]
