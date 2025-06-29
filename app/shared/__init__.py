from .logs import console
from .odm import MongoDbClient
from .sessions import SessionMiddleware
from .webpage import WebPage

__all__ = [MongoDbClient, SessionMiddleware, WebPage]

mclient = MongoDbClient()
