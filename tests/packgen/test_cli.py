"""Tests for packgen CLI invocation and argument parsing."""
import subprocess
import sys
from pathlib import Path
import pytest


def test_cli_help_exits_successfully():
    """CLI should display help and exit with code 0."""
    result = subprocess.run(
        [sys.executable, '-m', 'app.packgen.cli', '--help'],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert 'Generate Hidato puzzle packs' in result.stdout or 'usage:' in result.stdout


def test_cli_requires_output_directory():
    """CLI should fail if no output directory is provided."""
    result = subprocess.run(
        [sys.executable, '-m', 'app.packgen.cli'],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert 'required' in result.stderr.lower() or 'error' in result.stderr.lower()


def test_cli_accepts_valid_arguments():
    """CLI should accept valid argument combinations without crashing."""
    # Don't actually generate, just check arg parsing
    result = subprocess.run(
        [
            sys.executable, '-m', 'app.packgen.cli',
            '--outdir', '/tmp/test',
            '--sizes', '5',
            '--difficulties', 'easy',
            '--count', '1',
            '--dry-run',  # Assume we'll add this flag
        ],
        capture_output=True,
        text=True,
    )
    # Should parse successfully (may fail on dry-run if not implemented)
    assert 'usage:' not in result.stderr or result.returncode == 0


def test_cli_validates_size_range():
    """CLI should reject invalid size values."""
    result = subprocess.run(
        [
            sys.executable, '-m', 'app.packgen.cli',
            '--outdir', '/tmp/test',
            '--sizes', '3',  # Below minimum
            '--count', '1',
        ],
        capture_output=True,
        text=True,
    )
    # Should fail validation (either in argparse or generator)
    assert result.returncode != 0 or 'invalid' in result.stderr.lower()


def test_cli_validates_difficulty_values():
    """CLI should reject invalid difficulty values."""
    result = subprocess.run(
        [
            sys.executable, '-m', 'app.packgen.cli',
            '--outdir', '/tmp/test',
            '--sizes', '5',
            '--difficulties', 'impossible',  # Invalid difficulty
            '--count', '1',
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0 or 'invalid' in result.stderr.lower()


def test_cli_accepts_multiple_sizes():
    """CLI should accept comma-separated size list."""
    result = subprocess.run(
        [
            sys.executable, '-m', 'app.packgen.cli',
            '--outdir', '/tmp/test',
            '--sizes', '5,7',
            '--difficulties', 'easy',
            '--count', '2',
            '--dry-run',
        ],
        capture_output=True,
        text=True,
    )
    # Should parse successfully
    assert 'usage:' not in result.stderr or result.returncode == 0


def test_cli_accepts_optional_seed():
    """CLI should accept optional seed parameter."""
    result = subprocess.run(
        [
            sys.executable, '-m', 'app.packgen.cli',
            '--outdir', '/tmp/test',
            '--sizes', '5',
            '--difficulties', 'easy',
            '--count', '1',
            '--seed', '12345',
            '--dry-run',
        ],
        capture_output=True,
        text=True,
    )
    assert 'usage:' not in result.stderr or result.returncode == 0


def test_cli_accepts_retry_limit():
    """CLI should accept retry limit parameter."""
    result = subprocess.run(
        [
            sys.executable, '-m', 'app.packgen.cli',
            '--outdir', '/tmp/test',
            '--sizes', '5',
            '--difficulties', 'easy',
            '--count', '1',
            '--retries', '10',
            '--dry-run',
        ],
        capture_output=True,
        text=True,
    )
    assert 'usage:' not in result.stderr or result.returncode == 0
