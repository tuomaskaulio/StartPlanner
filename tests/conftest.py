"""Shared test paths."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"
SAMPLE_SMALL = SAMPLES / "sample-small"
SAMPLE_MEDIUM = SAMPLES / "sample-medium"
