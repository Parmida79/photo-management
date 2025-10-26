from typing import Any

from sqlalchemy.orm import mapped_column as column

# set column nullable default to False
def mapped_column(*args: Any, **kwargs: Any):
    """Wrapper around mapped_column with nullable=False by default."""
    kwargs.setdefault("nullable", False)
    return column(*args, **kwargs)

