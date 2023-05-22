from enum import Enum

from gtfs.utils.geom import Bbox


class Predicate(str, Enum):
    intersects = "intersects"
    contains = "contains"


# example inputs for testing geom funcs


bbox_covers_bbox = (Bbox(0, 0, 10, 10), Bbox(0, 0, 10, 10))
bbox_contained_inside_bbox = (Bbox(1, 1, 5, 5), Bbox(0, 0, 10, 10))
bbox_outside_bbox = (Bbox(15, 15, 20, 20), Bbox(0, 0, 10, 10))
bbox_intersecting_bbox = (Bbox(1, 1, 5, 5), Bbox(2, 2, 10, 15))
bbox_touches_edge_only_bbox = (Bbox(5, 1, 10, 5), Bbox(0, 0, 5, 15))

__all__ = [
    "bbox_covers_bbox",
    "bbox_contained_inside_bbox",
    "bbox_outside_bbox",
    "bbox_intersecting_bbox",
    "bbox_touches_edge_only_bbox",
]
