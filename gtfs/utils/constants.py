from enum import Enum


class Predicate(str, Enum):
    intersects = "intersects"
    contains = "contains"
