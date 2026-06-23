"""Vercel FastAPI entrypoint.

Deploy the ``backend`` directory as a separate Vercel project. Vercel detects
this module and serves the exported ASGI application with the Python runtime.
"""

from app.main import app

__all__ = ["app"]
