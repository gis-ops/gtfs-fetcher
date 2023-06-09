import pytest
from typer.testing import CliRunner

from gtfs.__main__ import app


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


class TestListFeedsCommand:
    def test_help(self, runner):
        result = runner.invoke(app, ["list-feeds", "--help"])
        assert result.exit_code == 0
        assert "Filter feeds spatially based on bounding box." in result.stdout

    def test_bad_args_1(self, runner):
        result = runner.invoke(app, ["list-feeds", "--bbox", "6.626953,49.423342,23.348144"])
        assert result.exit_code == 2
        assert "Please pass bbox as a string" in result.stdout

    def test_bad_args_2(self, runner):
        result = runner.invoke(app, ["list-feeds", "--bbox", "6.626953,49.423342,23.348144,fourteen"])
        assert result.exit_code == 2
        assert "Please pass only numbers as bbox values!" in result.stdout

    def test_bad_args_3(self, runner):
        result = runner.invoke(app, ["list-feeds", "--bbox", "6.626953,49.423342,6.626953,54.265953"])
        assert result.exit_code == 2
        assert "Area cannot be zero!" in result.stdout

    def test_intersects_predicate(self, runner):
        result = runner.invoke(
            app, ["list-feeds", "-pd", "intersects", "--bbox", "6.626953,49.423342,23.348144,54.265953"]
        )
        assert result.exit_code == 0

    def test_contains_predicate(self, runner):
        result = runner.invoke(
            app, ["list-feeds", "-pd", "contains", "--bbox", "6.626953,49.423342,23.348144,54.265953"]
        )
        assert result.exit_code == 0

    def test_pretty(self, runner):
        result = runner.invoke(app, ["list-feeds", "-pt"])
        assert result.exit_code == 0
