from pydantic import BaseModel, field_validator
from typing import Dict, Any
from enum import Enum

class BlockType(str, Enum):
    """Represents the types of blocks that make up the Minecraft world."""

    STONE = "stone"
    DIRT = "dirt"
    GRASS = "grass"
    SAND = "sand"
    WATER = "water"
    WOOD = "wood"
    LEAVES = "leaves"
    DIAMOND_ORE = "diamond_ore"
    GOLD_ORE = "gold_ore"
    COAL_ORE = "coal_ore"
    AIR = "air"
    GRAVEL = "gravel"
    LAPIS_LAZULI = "lapis_lazuli"
    REDSTONE_ORE = "redstone_ore"
    EMERALD_ORE = "emerald_ore"
    OBSIDIAN = "obsidian"
    BEDROCK = "bedrock"
    ICE = "ice"
    SNOW = "snow"
    CLAY = "clay"
    PUMPKIN = "pumpkin"
    MELON = "melon"

class Block(BaseModel):
    """Represents a single block in the Minecraft world."""

    x: int
    y: int
    z: int
    type: BlockType
    metadata: Dict[str, Any] = {}

    @field_validator("x", "y", "z")
    def validate_coordinates(cls, value):
        if value < 0:
            raise ValueError("Coordinates must be non-negative")
        return value

    @field_validator("type")
    def validate_block_type(cls, value):
        if not isinstance(value, BlockType):
            raise ValueError("Invalid block type")
        return value