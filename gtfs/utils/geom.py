class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def get_coords(feed_bbox: list[float], user_bbox: list[float]):
    feed_xmin, feed_ymin, feed_xmax, feed_ymax = feed_bbox
    user_xmin, user_ymin, user_xmax, user_ymax = user_bbox

    l1 = Point(feed_xmin, feed_ymax)  # top left coords of feed bbox
    r1 = Point(feed_xmax, feed_ymin)  # bottom right coords of feed bbox
    l2 = Point(user_xmin, user_ymax)  # top left coords of user bbox
    r2 = Point(user_xmax, user_ymin)  # bottom right coords of user bbox

    return [l1, r1, l2, r2]


def bbox_contains_bbox(feed_bbox: list[float], user_bbox: list[float]):
    """Check if feed_bbox is contained inside user_bbox."""
    l1, r1, l2, r2 = get_coords(feed_bbox, user_bbox)

    if (l1.x >= l2.x and r1.x <= r2.x) and (l1.y <= l2.y and r1.y >= r2.y):
        return True


def bbox_intersects_bbox(feed_bbox: list[float], user_bbox: list[float]):
    """Check if feed_bbox intersects user_bbox or vice-versa."""
    l1, r1, l2, r2 = get_coords(feed_bbox, user_bbox)

    # if rectangle has area 0, no overlap
    if l1.x == r1.x or l1.y == r1.y or r2.x == l2.x or l2.y == r2.y:
        return False

    # If one rectangle is on left side of other
    if l1.x > r2.x or l2.x > r1.x:
        return False

    # If one rectangle is above other
    if r1.y > l2.y or r2.y > l1.y:
        return False

    return True
