from hackproof.hackathon import get_hackathon, places


def test_awards_name_each_project_once():
    awards = get_hackathon().awards

    assert len({award.project_id for award in awards}) == len(awards)
    assert all(award.project_id.startswith("repo:") for award in awards)


def test_places_maps_every_award():
    assert places() == {award.project_id: award.place for award in get_hackathon().awards}
