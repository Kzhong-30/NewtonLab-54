from .auth import router as auth_router
from .scripts import router as scripts_router
from .games import router as games_router
from .reviews import router as reviews_router
from .dm import router as dm_router
from .community import router as community_router

__all__ = [
    "auth_router",
    "scripts_router",
    "games_router",
    "reviews_router",
    "dm_router",
    "community_router",
]
