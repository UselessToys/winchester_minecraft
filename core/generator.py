import noise
import random
from typing import List, Dict, Any
from .biome import BiomeType
from .block import Block, BlockType
from .entity import Entity, EntityType

def generate_advanced_landscape(
    width: int,
    height: int,
    scale: float = 50.0,
    octaves: int = 6,
    persistence: float = 0.5,
    lacunarity: float = 2.0,
    sea_level: float = 0.5,
    biome_scale: float = 200.0,
) -> List[List[Dict[str, Any]]]:
    """Generates a 2D landscape with biome data using Perlin noise and biome blending."""
    landscape = [
        [{"height": 0.0, "biome": None} for _ in range(width)] for _ in range(height)
    ]
    biome_map = [[0.0 for _ in range(width)] for _ in range(height)]

    # Generate base height map
    for y in range(height):
        for x in range(width):
            value = noise.pnoise2(
                x / scale,
                y / scale,
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
                repeatx=width,
                repeaty=height,
                base=0,
            )
            landscape[y][x]["height"] = (value + 1) / 2  # Normalize to 0-1

    # Generate biome map
    for y in range(height):
        for x in range(width):
            biome_value = noise.pnoise2(
                x / biome_scale,
                y / biome_scale,
                octaves=3,
                persistence=0.5,
                lacunarity=2.0,
                repeatx=width,
                repeaty=height,
                base=0,
            )
            biome_map[y][x] = (biome_value + 1) / 2  # Normalize to 0-1

    # Assign biomes based on biome map
    for y in range(height):
        for x in range(width):
            biome_value = biome_map[y][x]
            height_value = landscape[y][x]["height"]

            if height_value < sea_level:
                landscape[y][x]["biome"] = BiomeType.OCEAN
            elif biome_value < 0.3:
                landscape[y][x]["biome"] = BiomeType.DESERT
            elif biome_value < 0.6:
                landscape[y][x]["biome"] = BiomeType.PLAINS
            elif biome_value < 0.8:
                landscape[y][x]["biome"] = BiomeType.FOREST
            else:
                landscape[y][x]["biome"] = BiomeType.MOUNTAIN

    return landscape

def add_biome_features(
    landscape: List[List[Dict[str, Any]]],
    tree_density: float = 0.1,
    water_level: float = 0.3,
    cloud_density: float = 0.2,
) -> List[List[Dict[str, Any]]]:
    """Adds biome-specific features to the landscape such as trees, water, and clouds."""
    for y in range(len(landscape)):
        for x in range(len(landscape[0])):
            biome_type = landscape[y][x]["biome"]
            height_value = landscape[y][x]["height"]

            if biome_type == BiomeType.FOREST and random.random() < tree_density:
                landscape[y][x]["feature"] = "tree"
            elif height_value <= water_level:
                landscape[y][x]["feature"] = "water"
            elif random.random() < cloud_density:
                landscape[y][x]["feature"] = "cloud"

    return landscape

def create_block(
    x: int, y: int, z: int, block_type: BlockType, metadata: Dict[str, Any] = None
) -> Block:
    """Creates a new block with the given coordinates and type."""
    try:
        return Block(x=x, y=y, z=z, type=block_type, metadata=metadata or {})
    except ValueError as e:
        print(
            f"Error creating block at ({x}, {y}, {z}) of type {block_type}: {e}"
        )
        return None

def create_entity(
    x: int,
    y: int,
    z: int,
    entity_type: EntityType,
    health: int,
    attributes: Dict[str, Any] = None,
) -> Entity:
    """Creates a new entity with the given coordinates, type, and health."""
    try:
        return Entity(
            x=x, y=y, z=z, type=entity_type, health=health, attributes=attributes or {}
        )
    except ValueError as e:
        print(
            f"Error creating entity at ({x}, {y}, {z}) of type {entity_type} with health {health}: {e}"
        )
        return None