import pytest
from typer.testing import CliRunner

from gtfs.__main__ import app
from gtfs.utils.constants import *
from gtfs.utils.geom import bbox_contains_bbox, bbox_intersects_bbox


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


class Test_Geom_Functions:
    @pytest.mark.parametrize(
        "bbox1, bbox2",
        [bbox_covers_bbox, bbox_contained_inside_bbox],
    )
    def test_geom_contains(self, bbox1, bbox2):
        assert bbox_contains_bbox(bbox1, bbox2) == True

    @pytest.mark.parametrize(
        "bbox1, bbox2",
        [bbox_outside_bbox, bbox_intersecting_bbox],
    )
    def test_geom_contains_not(self, bbox1, bbox2):
        assert bbox_contains_bbox(bbox1, bbox2) == False

    @pytest.mark.parametrize(
        "bbox1, bbox2",
        [
            bbox_covers_bbox,
            bbox_contained_inside_bbox,
            bbox_intersecting_bbox,
            bbox_touches_edge_only_bbox,
        ],
    )
    def test_geom_intersects(self, bbox1, bbox2):
        assert bbox_intersects_bbox(bbox1, bbox2) or bbox_intersects_bbox(bbox2, bbox1) == True

    @pytest.mark.parametrize(
        "bbox1, bbox2",
        [bbox_outside_bbox],
    )
    def test_geom_intersects_not(self, bbox1, bbox2):
        assert bbox_intersects_bbox(bbox1, bbox2) or bbox_intersects_bbox(bbox2, bbox1) == False


class Test_List_Feeds_Command:
    def test_help(self, runner):
        result = runner.invoke(app, ["list-feeds", "--help"])
        assert result.exit_code == 0
        assert "Filter feeds spatially based on bounding box." in result.stdout

    def test_bad_args_1(self, runner):
        result = runner.invoke(app, ["list-feeds", "6.626953,49.423342,23.348144"])
        assert result.exit_code == 2
        assert "Please pass bbox as a string" in result.stdout

    def test_bad_args_2(self, runner):
        result = runner.invoke(app, ["list-feeds", "6.626953,49.423342,23.348144,fourteen"])
        assert result.exit_code == 2
        assert "Please pass only numbers as bbox values!" in result.stdout

    def test_bad_args_3(self, runner):
        result = runner.invoke(app, ["list-feeds", "6.626953,49.423342,6.626953,54.265953"])
        assert result.exit_code == 2
        assert "Area cannot be zero!" in result.stdout

    def test_intersects_predicate(self, runner):
        result = runner.invoke(app, ["list-feeds", "6.626953,49.423342,23.348144,54.265953"])
        assert result.exit_code == 0
        assert "Feeds based on bbox input" in result.stdout

    def test_contains_predicate(self, runner):
        result = runner.invoke(
            app, ["list-feeds", "-p", "contains", "6.626953,49.423342,23.348144,54.265953"]
        )
        assert result.exit_code == 0
        assert "Feeds based on bbox input" in result.stdout
