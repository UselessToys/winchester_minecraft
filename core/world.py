import random
from pydantic import BaseModel, field_validator
from typing import List, Dict
from .biome import Biome
from .entity import Entity

class World(BaseModel):
    """Represents the entire Minecraft world."""

    name: str
    biomes: List[Biome]
    time: int = 0
    weather: str = "clear"
    players: List[Entity] = []
    seed: int = random.randint(0, 1000000)
    gamerules: Dict[str, bool] = {
        "doDaylightCycle": True,
        "doWeatherCycle": True,
        "doMobSpawning": True,
    }

    @field_validator("name")
    def validate_name(cls, value):
        if not value:
            raise ValueError("Name cannot be empty")
        return value

    @field_validator("biomes")
    def validate_biomes(cls, value):
        if not value:
            raise ValueError("Biomes list cannot be empty")
        return value

    @field_validator("time")
    def validate_time(cls, value):
        if value < 0 or value > 24000:
            raise ValueError("Time must be between 0 and 24000")
        return value

    @field_validator("weather")
    def validate_weather(cls, value):
        if value not in ["clear", "rain", "thunder"]:
            raise ValueError("Invalid weather type")
        return value