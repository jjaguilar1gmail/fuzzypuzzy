"""Tests for generation report writer."""
import json
import pytest
from pathlib import Path
from app.packgen.report import GenerationReport, write_report


@pytest.fixture
def sample_report_data():
    """Sample generation statistics for report testing."""
    return {
        'pack_id': 'test-pack-20251111',
        'total_requested': 10,
        'total_generated': 8,
        'total_skipped': 1,
        'total_failed': 1,
        'difficulty_breakdown': {
            'easy': {'generated': 4, 'failed': 0},
            'medium': {'generated': 3, 'failed': 1},
            'hard': {'generated': 1, 'failed': 0},
        },
        'size_breakdown': {
            '5': 5,
            '7': 3,
        },
        'average_generation_time_ms': 245.3,
        'total_time_sec': 2.5,
        'metrics': {
            'generation_time_ms': {'avg': 200.0, 'min': 150.0, 'max': 260.0}
        },
    }


def test_generation_report_structure(sample_report_data, tmp_path):
    """Report should contain all expected summary fields."""
    report_file = tmp_path / "report.json"
    
    report = GenerationReport(**sample_report_data)
    write_report(report, report_file)
    
    assert report_file.exists()
    
    with open(report_file, 'r') as f:
        data = json.load(f)
    
    assert 'pack_id' in data
    assert 'total_requested' in data
    assert 'total_generated' in data
    assert 'total_skipped' in data
    assert 'total_failed' in data


def test_report_includes_difficulty_breakdown(sample_report_data, tmp_path):
    """Report should include per-difficulty statistics."""
    report_file = tmp_path / "report.json"
    
    report = GenerationReport(**sample_report_data)
    write_report(report, report_file)
    
    with open(report_file, 'r') as f:
        data = json.load(f)
    
    assert 'difficulty_breakdown' in data
    assert 'easy' in data['difficulty_breakdown']
    assert 'medium' in data['difficulty_breakdown']


def test_report_includes_timing_info(sample_report_data, tmp_path):
    """Report should include timing statistics."""
    report_file = tmp_path / "report.json"
    
    report = GenerationReport(**sample_report_data)
    write_report(report, report_file)
    
    with open(report_file, 'r') as f:
        data = json.load(f)
    
    assert 'average_generation_time_ms' in data
    assert 'total_time_sec' in data
    assert isinstance(data['average_generation_time_ms'], (int, float))
    assert isinstance(data['total_time_sec'], (int, float))


def test_report_calculates_success_rate(sample_report_data, tmp_path):
    """Report should calculate and include success rate."""
    report_file = tmp_path / "report.json"
    
    report = GenerationReport(**sample_report_data)
    write_report(report, report_file)
    
    with open(report_file, 'r') as f:
        data = json.load(f)
    
    # Success rate = generated / requested
    expected_rate = sample_report_data['total_generated'] / sample_report_data['total_requested']
    
    if 'success_rate' in data:
        assert abs(data['success_rate'] - expected_rate) < 0.01


def test_report_includes_metrics_block(sample_report_data, tmp_path):
    """Report JSON should include aggregate metrics when available."""
    report_file = tmp_path / "report.json"
    report = GenerationReport(**sample_report_data)
    write_report(report, report_file)

    with open(report_file, 'r') as f:
        data = json.load(f)

    assert 'metrics' in data
    assert 'generation_time_ms' in data['metrics']


def test_report_human_readable_output(sample_report_data, tmp_path):
    """Report should generate human-readable text summary."""
    report_file = tmp_path / "report.txt"
    
    report = GenerationReport(**sample_report_data)
    write_report(report, report_file, format='text')
    
    assert report_file.exists()
    
    content = report_file.read_text()
    
    # Should contain key statistics in readable form
    assert 'test-pack' in content
    assert '8' in content  # total generated
    assert '10' in content  # total requested


def test_report_json_is_valid(sample_report_data, tmp_path):
    """Report JSON should be parseable."""
    report_file = tmp_path / "report.json"
    
    report = GenerationReport(**sample_report_data)
    write_report(report, report_file)
    
    # Should be able to re-parse
    with open(report_file, 'r') as f:
        data = json.load(f)
    
    assert isinstance(data, dict)
    assert len(data) > 0
