from pydantic import BaseModel, field_validator
from typing import Dict, Any
from enum import Enum

class EntityType(str, Enum):
    """Represents the types of entities that can exist in the Minecraft world."""

    CREEPER = "creeper"
    ZOMBIE = "zombie"
    SKELETON = "skeleton"
    SPIDER = "spider"
    ENDERMAN = "enderman"
    PLAYER = "player"
    VILLAGER = "villager"
    WITCH = "witch"
    GHAST = "ghast"
    SLIME = "slime"
    GUARDIAN = "guardian"
    SHULKER = "shulker"
    PIG = "pig"
    COW = "cow"
    SHEEP = "sheep"
    CHICKEN = "chicken"
    HORSE = "horse"
    WOLF = "wolf"
    OCELOT = "ocelot"

class Entity(BaseModel):
    """Represents an entity in the Minecraft world."""

    x: int
    y: int
    z: int
    type: EntityType
    health: int
    attributes: Dict[str, Any] = {}

    @field_validator("x", "y", "z")
    def validate_coordinates(cls, value):
        if value < 0:
            raise ValueError("Coordinates must be non-negative")
        return value

    @field_validator("type")
    def validate_entity_type(cls, value):
        if not isinstance(value, EntityType):
            raise ValueError("Invalid entity type")
        return value

    @field_validator("health")
    def validate_health(cls, value):
        if value < 0:
            raise ValueError("Health must be non-negative")
        return value