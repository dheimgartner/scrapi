"""
Optional import to suppress known, harmless third-party warnings.

Usage:
    import conflict_checker.warnings_suppression  # noqa: F401

Import this BEFORE any module that triggers the warnings below, since the
filters only apply to warnings emitted after they're registered.
"""

import warnings

# pydub: fires at import time via markitdown -> audio converter,
# even though we never use audio transcription.
warnings.filterwarnings(
    "ignore",
    message="Couldn't find ffmpeg or avconv",
    category=RuntimeWarning,
)
