"""Unit tests for the curriculum engine (scripts/curriculum.py).

Two tiers: pure-function tests on constructed inputs (the new registry/drift
logic), and integration assertions that the real repo's sources are
internally consistent — the same invariants the CI drift gate enforces.
"""

from __future__ import annotations

import curriculum
import pytest


def make_notebook(path: str, *, library: str, track: str | None = None, rung: str | None = None):
    """Build a minimal Notebook for pure-logic tests."""
    return curriculum.Notebook(
        path=path,
        domain=path.split("/")[1],
        library=library,
        seq=1,
        title="t",
        summary="s",
        track=track,
        rung=rung,
        packages=[],
        requires_python=None,
        headings=[],
        has_tests=False,
        upstream_url=None,
    )


def make_track(track_id: str, *, notebooks=()):
    return curriculum.Track(
        id=track_id,
        topic="topic",
        mastery="fundamentals",
        status="seed",
        notebooks=list(notebooks),
    )


# --- pure registry/drift logic -------------------------------------------------


class TestLibraryProjectErrors:
    def test_unregistered_library_is_an_error(self):
        nbs = [make_notebook("notebooks/data/polars/001_x.py", library="polars")]
        errors = curriculum.library_project_errors(nbs, projects=[])
        assert len(errors) == 1
        assert "polars" in errors[0]

    def test_registered_library_is_clean(self):
        nbs = [make_notebook("notebooks/data/polars/001_x.py", library="polars")]
        projects = [curriculum.Project(name="polars", tracks=["data/dataframes"])]
        assert curriculum.library_project_errors(nbs, projects) == []


class TestProjectTrackErrors:
    def test_unknown_track_reference_is_an_error(self):
        tracks = [make_track("data/dataframes")]
        projects = [curriculum.Project(name="polars", tracks=["data/dataframes", "nope/missing"])]
        errors = curriculum.project_track_errors(tracks, projects)
        assert len(errors) == 1
        assert "nope/missing" in errors[0]

    def test_known_track_reference_is_clean(self):
        tracks = [make_track("data/dataframes"), make_track("data/query-engines")]
        projects = [curriculum.Project(name="duckdb", tracks=["data/query-engines"])]
        assert curriculum.project_track_errors(tracks, projects) == []


def test_claims_resolves_many_to_many():
    nb = "notebooks/data/pyarrow/001_x.py"
    t1 = make_track("data/distributed", notebooks=[{"path": nb}])
    t2 = make_track("data/storage-formats", notebooks=[{"path": nb}])
    claimed = curriculum.claims([t1, t2])
    assert {t.id for t in claimed[nb]} == {"data/distributed", "data/storage-formats"}


def test_notebook_rungs_maps_paths_to_words():
    track = make_track(
        "data/dataframes",
        notebooks=[
            {"path": "notebooks/data/numpy/001_x.py", "rung": "fundamentals"},
            {"path": "notebooks/data/pandas/001_x.py", "rung": "self-sufficiency"},
        ],
    )
    rungs = curriculum.notebook_rungs([track])
    assert rungs["notebooks/data/numpy/001_x.py"] == "fundamentals"
    assert rungs["notebooks/data/pandas/001_x.py"] == "self-sufficiency"


# --- the real repo's sources are internally consistent -------------------------


@pytest.fixture(scope="module")
def repo():
    notebooks, tracks = curriculum.index()
    return notebooks, tracks, curriculum.load_projects()


def test_real_repo_has_no_drift_errors():
    result = curriculum.check_drift()
    assert result.errors == []


def test_every_notebook_library_has_a_project(repo):
    notebooks, _, projects = repo
    assert curriculum.library_project_errors(notebooks, projects) == []


def test_every_project_points_at_a_real_track(repo):
    _, tracks, projects = repo
    assert curriculum.project_track_errors(tracks, projects) == []


def test_registry_counts(repo):
    notebooks, tracks, projects = repo
    assert len(notebooks) == 23
    assert len(tracks) == 22
    assert len(projects) == 46


def test_known_project_fields():
    projects = {p.name: p for p in curriculum.load_projects()}
    polars = projects["polars"]
    assert polars.upstream == "https://github.com/pola-rs/polars"
    assert polars.tracks == ["data/dataframes", "systems/rust-in-python"]
    assert polars.rust_in_python == "rust-core-frontend"


def test_parse_notebook_extracts_library_and_upstream():
    nb = curriculum.parse_notebook(
        curriculum.REPO_ROOT / "notebooks/toolchain/marimo/001_basics.py"
    )
    assert nb.library == "marimo"
    assert nb.upstream_url == "https://github.com/marimo-team/marimo"
    assert not hasattr(nb, "clone_path")


# --- the committed source map is portable and shape-valid -----------------------


def test_committed_source_map_passes_shape_validation(repo):
    _, _, projects = repo
    assert curriculum.source_map_errors(projects) == []


def test_source_map_records_are_pinned_portable_urls():
    """Every committed row is a version-pinned github blob URL — no local paths."""
    import json

    lines = curriculum.SOURCES.read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in lines if line.strip()]
    assert records, "expected a committed source map"
    names = {p.name for p in curriculum.load_projects()}
    for rec in records:
        assert rec["project"] in names
        assert rec["url"].startswith("https://github.com/") and "/blob/" in rec["url"]
        assert f"/blob/{rec['tag']}/" in rec["url"]  # the URL is pinned to its tag
        assert "/home/" not in rec["url"]
