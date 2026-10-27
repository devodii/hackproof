from hackproof.github.repositories import candidate_from_node

NODE = {
    "nameWithOwner": "team/app",
    "url": "https://github.com/team/app",
    "description": "an app",
    "stargazerCount": 3,
    "forkCount": 1,
    "isFork": False,
    "createdAt": "2026-10-25T12:00:00Z",
    "pushedAt": "2026-10-26T08:00:00Z",
    "homepageUrl": "",
    "primaryLanguage": {"name": "Rust"},
    "licenseInfo": {"spdxId": "MIT"},
    "defaultBranchRef": {
        "name": "main",
        "target": {
            "total": {"totalCount": 40},
            "inWindow": {"totalCount": 31},
            "before": {"nodes": [{"oid": "abc123"}]},
        },
    },
    "owner": {"login": "team", "avatarUrl": "https://avatars/x", "location": "Lisbon, Portugal"},
    "repositoryTopics": {"nodes": [{"topic": {"name": "stellar"}}]},
}


def test_node_carries_commit_counts_base_commit_and_owner_location():
    candidate = candidate_from_node(NODE)
    assert (candidate.total_commits, candidate.window_commits) == (40, 31)
    assert candidate.base_sha == "abc123"
    assert candidate.owner_location == "Lisbon, Portugal"
    assert (candidate.language, candidate.license, candidate.forks) == ("Rust", "MIT", 1)
    assert candidate.topics == ["stellar"]
    assert candidate.homepage is None


def test_empty_repo_has_no_branch_or_counts():
    candidate = candidate_from_node({**NODE, "defaultBranchRef": None, "primaryLanguage": None})
    assert candidate.default_branch is None
    assert candidate.total_commits is None and candidate.base_sha is None
    assert candidate.language is None


def test_repo_with_no_commit_before_the_window_has_no_base():
    target = {"total": {"totalCount": 5}, "inWindow": {"totalCount": 5}, "before": {"nodes": []}}
    candidate = candidate_from_node(
        {**NODE, "defaultBranchRef": {"name": "main", "target": target}}
    )
    assert candidate.base_sha is None
