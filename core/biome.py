from pydantic import BaseModel, field_validator
from typing import List
from enum import Enum
from .block import Block
from .entity import Entity

class BiomeType(str, Enum):
    """Represents the type of biome in the Minecraft world."""

    PLAINS = "plains"
    FOREST = "forest"
    DESERT = "desert"
    OCEAN = "ocean"
    MOUNTAIN = "mountain"
    TUNDRA = "tundra"
    SAVANNA = "savanna"
    SWAMP = "swamp"
    TAIGA = "taiga"
    JUNGLE = "jungle"

class Biome(BaseModel):
    """Represents a biome in the Minecraft world."""

    name: str
    type: BiomeType
    blocks: List[Block]
    entities: List[Entity]
    temperature: float
    humidity: float

    @field_validator("name")
    def validate_name(cls, value):
        if not value:
            raise ValueError("Name cannot be empty")
        return value

    @field_validator("type")
    def validate_biome_type(cls, value):
        if not isinstance(value, BiomeType):
            raise ValueError("Invalid biome type")
        return value

    @field_validator("blocks")
    def validate_blocks(cls, value):
        if not value:
            raise ValueError("Blocks list cannot be empty")
        return value

    @field_validator("entities")
    def validate_entities(cls, value):
        if not value:
            raise ValueError("Entities list cannot be empty")
        return value

    @field_validator("temperature")
    def validate_temperature(cls, value):
        if value < -1.0 or value > 2.0:
            raise ValueError("Temperature must be between -1.0 and 2.0")
        return value

    @field_validator("humidity")
    def validate_humidity(cls, value):
        if value < 0.0 or value > 1.0:
            raise ValueError("Humidity must be between 0.0 and 1.0")
        return value