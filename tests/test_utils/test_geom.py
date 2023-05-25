import pytest

from gtfs.utils.geom import Bbox, bbox_contains_bbox, bbox_intersects_bbox


class Test_Geom_Functions:
    @pytest.mark.parametrize(
        # 1. bbox1 is covering bbox2;
        # 2. bbox1 is contained in bbox2;
        "bbox1, bbox2",
        [(Bbox(0, 0, 10, 10), Bbox(0, 0, 10, 10)), (Bbox(1, 1, 5, 5), Bbox(0, 0, 10, 10))],
    )
    def test_geom_contains(self, bbox1, bbox2):
        assert bbox_contains_bbox(bbox1, bbox2) is True

    @pytest.mark.parametrize(
        # 1. bbox1 is outside bbox2;
        # 2. bbox1 and bbox2 are intersecting but bbox1 is not contained in bbox2;
        "bbox1, bbox2",
        [(Bbox(15, 15, 20, 20), Bbox(0, 0, 10, 10)), (Bbox(1, 1, 5, 5), Bbox(2, 2, 10, 15))],
    )
    def test_geom_contains_not(self, bbox1, bbox2):
        assert bbox_contains_bbox(bbox1, bbox2) is False

    @pytest.mark.parametrize(
        # 1. bbox1 is covering bbox2;
        # 2. bbox1 is contained in bbox2;
        # 3. bbox1 and bbox2 are intersecting but bbox1 is not contained in bbox2;
        # 4. bbox1 touches edge of bbox2;
        "bbox1, bbox2",
        [
            (Bbox(0, 0, 10, 10), Bbox(0, 0, 10, 10)),
            (Bbox(1, 1, 5, 5), Bbox(0, 0, 10, 10)),
            (Bbox(1, 1, 5, 5), Bbox(2, 2, 10, 15)),
            (Bbox(5, 1, 10, 5), Bbox(0, 0, 5, 15)),
        ],
    )
    def test_geom_intersects(self, bbox1, bbox2):
        assert (bbox_intersects_bbox(bbox1, bbox2) or bbox_intersects_bbox(bbox2, bbox1)) is True

    @pytest.mark.parametrize(
        # 1. bbox1 is outside bbox2;
        "bbox1, bbox2",
        [(Bbox(15, 15, 20, 20), Bbox(0, 0, 10, 10))],
    )
    def test_geom_intersects_not(self, bbox1, bbox2):
        assert (bbox_intersects_bbox(bbox1, bbox2) or bbox_intersects_bbox(bbox2, bbox1)) is False
