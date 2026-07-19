import math
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    # JSON naturally represents enums and timestamps as strings. Individual fields retain
    # explicit bounds/validators while unknown fields are always rejected.
    model_config = ConfigDict(extra="forbid")


class ClientRole(StrEnum):
    HOST = "host"
    DEVICE = "device"
    DASHBOARD = "dashboard"


class Keypoint(StrictModel):
    id: int = Field(ge=0, le=1_024)
    x: float
    y: float
    confidence: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def finite_coordinates(self) -> "Keypoint":
        if not math.isfinite(self.x) or not math.isfinite(self.y):
            raise ValueError("keypoint coordinates must be finite")
        return self


class ImageMetadata(StrictModel):
    width: int = Field(ge=1, le=16_384)
    height: int = Field(ge=1, le=16_384)
    rotation_degrees: int = Field(default=0)
    mirrored: bool = False

    @model_validator(mode="after")
    def valid_rotation(self) -> "ImageMetadata":
        if self.rotation_degrees not in {0, 90, 180, 270}:
            raise ValueError("rotation_degrees must be 0, 90, 180, or 270")
        return self
