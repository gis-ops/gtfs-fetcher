from collections import namedtuple

Bbox = namedtuple("Bbox", ["min_x", "min_y", "max_x", "max_y"])


def bbox_contains_bbox(bbox1: Bbox, bbox2: Bbox) -> bool:
    """Check if bbox1 is contained inside bbox2."""
    if (bbox1.min_x >= bbox2.min_x and bbox1.max_x <= bbox2.max_x) and (
        bbox1.max_y <= bbox2.max_y and bbox1.min_y >= bbox2.min_y
    ):
        return True


def bbox_intersects_bbox(bbox1: Bbox, bbox2: Bbox) -> bool:
    """Check if bbox1 intersects bbox2"""
    # checks if bbox1 is ahead or behind of bbox2
    if bbox1.min_x > bbox2.max_x or bbox1.max_x < bbox2.min_x:
        return False
    # checks if bbox1 is above or below of bbox2
    elif bbox1.min_y > bbox2.max_y or bbox1.max_y < bbox2.min_y:
        return False

    return True
