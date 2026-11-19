import pytest

from hackproof.pipeline import Options, select, stages


def names(**kwargs) -> list[str]:
    return [stage.name for stage in select(stages(Options()), **kwargs)]


def test_the_pipeline_runs_every_stage_in_order_by_default():
    assert names() == ["sync", "discover", "scan", "reconcile", "observe", "export"]


def test_it_can_start_part_way_or_leave_stages_out():
    assert names(start="reconcile") == ["reconcile", "observe", "export"]
    assert names(skip=["discover", "scan"]) == [
        "sync",
        "reconcile",
        "observe",
        "export",
    ]
    assert names(only=["export", "sync"]) == ["sync", "export"]


def test_an_unknown_stage_is_refused_with_the_valid_ones():
    with pytest.raises(ValueError, match="unknown stage nope"):
        names(skip=["nope"])
