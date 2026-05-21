"""Declarative base used by all PostgreSQL ORM models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
	"""Shared declarative base for the SQLAlchemy model layer."""
    pass