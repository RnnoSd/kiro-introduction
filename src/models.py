from dataclasses import dataclass


@dataclass
class Vector2:
    """2D vector with x and y float components."""
    x: float
    y: float


@dataclass
class Rect:
    """Axis-Aligned Bounding Box.

    x: left edge
    y: top edge
    width: horizontal extent
    height: vertical extent
    """
    x: float
    y: float
    width: float
    height: float


def rects_overlap(a: Rect, b: Rect) -> bool:
    """Return True if two rectangles overlap.

    Touching edges are NOT considered a collision (strict inequality).
    """
    return (
        a.x < b.x + b.width and a.x + a.width > b.x and
        a.y < b.y + b.height and a.y + a.height > b.y
    )
