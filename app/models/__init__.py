# In app/models/__init__.py

from .user import User
from .anime import Anime, Rating

# This line is optional but good practice. It defines the public API of the package.
__all__ = ['User', 'Anime', 'Rating']