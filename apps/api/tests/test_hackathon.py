from hackproof.cli import main
from hackproof.config import get_settings
from hackproof.hackathon import get_hackathon, places


def test_awards_name_each_project_once():
    awards = get_hackathon().awards

    assert len({award.project_id for award in awards}) == len(awards)
    assert all(award.project_id.startswith("repo:") for award in awards)


def test_places_maps_every_award():
    assert places() == {award.project_id: award.place for award in get_hackathon().awards}


def test_new_hackathon_with_flags_writes_yaml_that_loads_through_get_hackathon(
    tmp_path, monkeypatch, capsys
):
    main(
        [
            "new-hackathon",
            "--slug",
            "hackmeridian-2027",
            "--name",
            "HackMeridian 2027",
            "--start",
            "2027-10-25T09:00:00Z",
            "--end",
            "2027-10-26T12:00:00Z",
            "--output-dir",
            str(tmp_path),
        ]
    )
    out = capsys.readouterr().out
    yaml_path = tmp_path / "hackmeridian-2027.yaml"
    assert yaml_path.exists()
    assert "uv run hackproof sync" in out

    monkeypatch.setenv("HACKPROOF_HACKATHON_FILE", str(yaml_path))
    get_settings.cache_clear()
    get_hackathon.cache_clear()
    try:
        loaded = get_hackathon()
        assert loaded.slug == "hackmeridian-2027"
        assert loaded.name == "HackMeridian 2027"
        assert "topic:hackmeridian" in loaded.discovery.github_queries
        assert '"hackmeridian 2027" in:name,description,readme' in loaded.discovery.github_queries
    finally:
        get_settings.cache_clear()
        get_hackathon.cache_clear()
