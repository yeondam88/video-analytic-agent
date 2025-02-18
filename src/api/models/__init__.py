"""Models for the API.

This module is a proxy to the actual models defined in src.db.models.
All model imports should be done from src.db.models directly.
"""

from src.db.models import Base, Video, Segment

__all__ = ["Base", "Video", "Segment"] 