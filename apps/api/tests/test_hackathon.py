from hackproof.hackathon import get_hackathon, hackathons


def test_awards_name_each_project_once():
    awards = get_hackathon().awards

    assert len({award.project_id for award in awards}) == len(awards)
    assert all(award.project_id.startswith("repo:") for award in awards)


def test_places_maps_every_award():
    assert get_hackathon().places() == {
        award.project_id: award.place for award in get_hackathon().awards
    }


def test_every_hackathon_folder_is_found_by_its_id():
    assert get_hackathon().slug in hackathons()
    assert all(slug == item.slug for slug, item in hackathons().items())
