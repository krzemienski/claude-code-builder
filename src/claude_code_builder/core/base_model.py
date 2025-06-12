"""Base model for all Pydantic models in Claude Code Builder."""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field


class BaseModel(PydanticBaseModel):
    """Base model with common configuration for all models."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        validate_assignment=True,
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        },
    )


class TimestampedModel(BaseModel):
    """Base model with timestamp fields."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


class IdentifiedModel(TimestampedModel):
    """Base model with ID and timestamp fields."""

    id: UUID = Field(default_factory=uuid4)


class NamedModel(IdentifiedModel):
    """Base model with ID, name, and description."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class MetadataModel(BaseModel):
    """Base model for objects that can have arbitrary metadata."""

    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_metadata(self, key: str, value: Any) -> None:
        """Add a metadata entry."""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get a metadata value."""
        return self.metadata.get(key, default)

    def remove_metadata(self, key: str) -> Any:
        """Remove and return a metadata value."""
        return self.metadata.pop(key, None)