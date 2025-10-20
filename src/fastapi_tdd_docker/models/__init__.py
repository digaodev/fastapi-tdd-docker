from sqlmodel import SQLModel  # re-export for Alembic

from .text_summary import TextSummary  # ensure table is registered on metadata

__all__ = ["SQLModel", "TextSummary"]
