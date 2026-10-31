from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml

from hackproof.hackathon import Hackathon
from hackproof.scaffold import create_hackathon_config, parse_datetime


def test_parse_datetime():
    dt1 = parse_datetime("2027-05-15T10:00:00Z")
    assert dt1 == datetime(2027, 5, 15, 10, 0, 0, tzinfo=UTC)

    dt2 = parse_datetime("2027-05-15")
    assert dt2 == datetime(2027, 5, 15, 0, 0, 0, tzinfo=UTC)


def test_create_hackathon_config(tmp_path: Path):
    out_file = tmp_path / "hacklisbon-2027.yaml"
    dest = create_hackathon_config(
        slug="hacklisbon-2027",
        name="HackLisbon 2027",
        start_str="2027-04-10T09:00:00Z",
        end_str="2027-04-11T18:00:00Z",
        output_path=out_file,
    )

    assert dest == out_file
    assert out_file.exists()

    with out_file.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Acceptance criteria: Must load and validate through Hackathon model
    hackathon = Hackathon.model_validate(data)
    assert hackathon.slug == "hacklisbon-2027"
    assert hackathon.name == "HackLisbon 2027"
    assert hackathon.window.start == datetime(2027, 4, 10, 9, 0, tzinfo=UTC)
    assert hackathon.window.end == datetime(2027, 4, 11, 18, 0, tzinfo=UTC)
    # Default pull_start is 1 hour before start
    assert hackathon.window.pull_start == datetime(2027, 4, 10, 8, 0, tzinfo=UTC)

    # Discovery queries derived from slug and name
    queries = hackathon.discovery.github_queries
    assert any("hacklisbon-2027" in q for q in queries)
    assert any("HackLisbon 2027" in q for q in queries)
    assert "topic:hacklisbon-2027" in queries
    assert "stellar in:name,description,readme,topics" in queries


def test_create_hackathon_invalid_dates(tmp_path: Path):
    out_file = tmp_path / "invalid.yaml"
    with pytest.raises(ValueError, match="must be after"):
        create_hackathon_config(
            slug="invalid-dates",
            name="Invalid Dates",
            start_str="2027-04-11T18:00:00Z",
            end_str="2027-04-10T09:00:00Z",
            output_path=out_file,
        )
