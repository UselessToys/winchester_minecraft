import sys
import random
import time
import noise
from pydantic import BaseModel, field_validator, ValidationError
from typing import List, Tuple
from enum import Enum
import math
import logging
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QSlider, QComboBox, QMainWindow, QSizePolicy, QFileDialog, QMessageBox)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QTimer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Sonnet ---
sonnet = """In blocky worlds where pixels intertwine,
My heart, a compass, always points to thee,
Through verdant plains and caves, your light doth shine,
A beacon in this game, eternally.

We build our castles 'neath the square-shaped sun,
And face the creepers with a diamond sword,
In every battle fought, in every one,
My love for you, my dear, is my reward.

The endless biomes stretch far and wide,
Yet none compare to when you're by my side,
Together we explore, with naught to hide,
In this Minecraftian love, we do abide.

So let us craft our tale in this vast land,
Forever joined, a pickaxe in each hand."""

# --- Essay ---
essay = """
Dean Winchester: A Study in Heroism and Humanity

Dean Winchester, the elder of the Winchester brothers in the CW series "Supernatural,"
is a character study in contradictions and complexities. On the surface, he is the
quintessential American hero: brave, self-sacrificing, and fiercely loyal. Yet, beneath
this rugged exterior lies a man haunted by his past, burdened by responsibility, and
often struggling with his own inner demons.

Dean's life is defined by the hunt. From a young age, he was thrust into a world of
monsters and mayhem, a world where his childhood was stolen by the very creatures he
was trained to kill. This upbringing forged him into a warrior, but it also left deep
scars. Dean's dedication to his family, particularly his younger brother Sam, is his
driving force. He sees himself as Sam's protector, a role he embraces with unwavering
commitment, even at great personal cost.

Dean's character is not without flaws. He can be reckless, impulsive, and at times,
self-destructive. His coping mechanisms often involve a bottle of whiskey and a
devil-may-care attitude. Yet, these flaws only serve to make him more human, more
relatable. Dean is not a perfect hero; he is a man who has been shaped by tragedy
and who fights every day to keep the darkness at bay, both within and without.

One of the most compelling aspects of Dean's character is his capacity for love and
loyalty. Despite the horrors he has witnessed and the losses he has endured, Dean
never loses his ability to care deeply for those he loves. His relationships with
Sam, Castiel, and other allies are the heart of the show, providing moments of
tenderness and humor amidst the darkness.

In conclusion, Dean Winchester is more than just a hunter of monsters. He is a son,
a brother, a friend, and a hero. He embodies the struggle between good and evil,
light and darkness, and his journey is a testament to the resilience of the human
spirit. Dean Winchester's story is a reminder that even in the face of unimaginable
adversity, hope, love, and a little bit of rock 'n' roll can carry us through.
"""

# --- Enumerations ---

class BiomeType(str, Enum):
    """Represents the type of biome in the Minecraft world."""
    PLAINS = "plains"
    FOREST = "forest"
    DESERT = "desert"
    OCEAN = "ocean"
    MOUNTAIN = "mountain"

class EntityType(str, Enum):
    """Represents the types of entities that can exist in the Minecraft world."""
    CREEPER = "creeper"
    ZOMBIE = "zombie"
    SKELETON = "skeleton"
    SPIDER = "spider"
    ENDERMAN = "enderman"
    PLAYER = "player"
    VILLAGER = "villager"

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

# --- Pydantic Models ---

class Block(BaseModel):
    """Represents a single block in the Minecraft world."""
    x: int
    y: int
    z: int
    type: BlockType

    @field_validator('x', 'y', 'z')
    def validate_coordinates(cls, value):
        if value < 0:
            raise ValueError("Coordinates must be non-negative")
        return value

    @field_validator('type')
    def validate_block_type(cls, value):
        if not isinstance(value, BlockType):
            raise ValueError("Invalid block type")
        return value

class Entity(BaseModel):
    """Represents an entity in the Minecraft world."""
    x: int
    y: int
    z: int
    type: EntityType
    health: int

    @field_validator('x', 'y', 'z')
    def validate_coordinates(cls, value):
        if value < 0:
            raise ValueError("Coordinates must be non-negative")
        return value

    @field_validator('type')
    def validate_entity_type(cls, value):
        if not isinstance(value, EntityType):
            raise ValueError("Invalid entity type")
        return value

    @field_validator('health')
    def validate_health(cls, value):
        if value < 0:
            raise ValueError("Health must be non-negative")
        return value

class Biome(BaseModel):
    """Represents a biome in the Minecraft world."""
    name: str
    type: BiomeType
    blocks: List[Block]
    entities: List[Entity]

    @field_validator('name')
    def validate_name(cls, value):
        if not value:
            raise ValueError("Name cannot be empty")
        return value

    @field_validator('type')
    def validate_biome_type(cls, value):
        if not isinstance(value, BiomeType):
            raise ValueError("Invalid biome type")
        return value

    @field_validator('blocks')
    def validate_blocks(cls, value):
        if not value:
            raise ValueError("Blocks list cannot be empty")
        return value

    @field_validator('entities')
    def validate_entities(cls, value):
        if not value:
            raise ValueError("Entities list cannot be empty")
        return value

class World(BaseModel):
    """Represents the entire Minecraft world."""
    name: str
    biomes: List[Biome]
    time: int = 0
    weather: str = "clear"

    @field_validator('name')
    def validate_name(cls, value):
        if not value:
            raise ValueError("Name cannot be empty")
        return value

    @field_validator('biomes')
    def validate_biomes(cls, value):
        if not value:
            raise ValueError("Biomes list cannot be empty")
        return value

    @field_validator('time')
    def validate_time(cls, value):
        if value < 0 or value > 24000:
            raise ValueError("Time must be between 0 and 24000")
        return value

    @field_validator('weather')
    def validate_weather(cls, value):
        if value not in ["clear", "rain", "thunder"]:
            raise ValueError("Invalid weather type")
        return value

# --- Helper Functions ---

def create_block(x: int, y: int, z: int, block_type: BlockType) -> Block:
    """Creates a new block with the given coordinates and type."""
    try:
        return Block(x=x, y=y, z=z, type=block_type)
    except ValueError as e:
        logging.error(f"Error creating block at ({x}, {y}, {z}) of type {block_type}: {e}")
        return None

def create_entity(x: int, y: int, z: int, entity_type: EntityType, health: int) -> Entity:
    """Creates a new entity with the given coordinates, type, and health."""
    try:
        return Entity(x=x, y=y, z=z, type=entity_type, health=health)
    except ValueError as e:
        logging.error(f"Error creating entity at ({x}, {y}, {z}) of type {entity_type} with health {health}: {e}")
        return None

def create_biome(name: str, biome_type: BiomeType, blocks: List[Block], entities: List[Entity]) -> Biome:
    """Creates a new biome with the given name, type, blocks, and entities."""
    try:
        return Biome(name=name, type=biome_type, blocks=blocks, entities=entities)
    except ValueError as e:
        logging.error(f"Error creating biome '{name}' of type {biome_type}: {e}")
        return None

def create_world(name: str, biomes: List[Biome]) -> World:
    """Creates a new world with the given name and biomes."""
    try:
        return World(name=name, biomes=biomes)
    except ValueError as e:
        logging.error(f"Error creating world '{name}': {e}")
        return None

# --- Landscape Generation Functions ---

def generate_landscape(width: int, height: int, scale: float = 10.0, octaves: int = 6, persistence: float = 0.5,
                       lacunarity: float = 2.0) -> List[List[float]]:
    """Generates a 2D landscape using Perlin noise."""
    landscape = [[0.0 for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            value = noise.pnoise2(x / scale,
                                  y / scale,
                                  octaves=octaves,
                                  persistence=persistence,
                                  lacunarity=lacunarity,
                                  repeatx=width,
                                  repeaty=height,
                                  base=0)
            landscape[y][x] = (value + 1) / 2  # Normalize to 0-1
    return landscape

def add_trees(landscape: List[List[float]], tree_density: float = 0.1) -> List[List[float]]:
    """Adds trees to the landscape based on the given density."""
    for y in range(len(landscape)):
        for x in range(len(landscape[0])):
            if landscape[y][x] > 0 and random.random() < tree_density:
                landscape[y][x] = -1  # Mark as tree
    return landscape

def add_water(landscape: List[List[float]], water_level: float = 0.3) -> List[List[float]]:
    """Adds water to the landscape based on the given water level."""
    for y in range(len(landscape)):
        for x in range(len(landscape[0])):
            if 0 < landscape[y][x] <= water_level:
                landscape[y][x] = -2  # Mark as water
    return landscape

def add_clouds(landscape: List[List[float]], cloud_density: float = 0.2) -> List[List[float]]:
    """Adds clouds to the landscape based on the given density."""
    cloud_map = generate_landscape(len(landscape[0]), len(landscape), scale=20.0)
    for y in range(len(landscape)):
        for x in range(len(landscape[0])):
            if cloud_map[y][x] >= 0.7 and random.random() < cloud_density:
                if landscape[y][x] >= 0:
                    landscape[y][x] = -3  # Mark as cloud
    return landscape

# --- GUI and Rendering ---

class LandscapeWidget(QWidget):
    """Widget for rendering the Minecraft landscape."""
    def __init__(self, width: int, height: int):
        super().__init__()
        self.width = width
        self.height = height
        self.landscape = None
        self.image = QImage(self.width, self.height, QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white)
        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(self.width, self.height)

    def set_landscape(self, landscape: List[List[float]]):
        self.landscape = landscape
        self.update_image()
        self.update()

    def update_image(self):
        if self.landscape is None:
            return

        for y in range(self.height):
            for x in range(self.width):
                value = self.landscape[y][x]
                if value == -1:  # Tree
                    color = QColor("green")
                elif value == -2:  # Water
                    color = QColor("blue")
                elif value == -3:  # Cloud
                    color = QColor("white")
                elif value == 0:
                    color = QColor("white")
                else:
                    # Terrain shading
                    shade = int(value * 255)
                    color = QColor(shade, shade, shade)
                self.image.setPixelColor(x, y, color)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(self.rect(), self.image)

class MainWindow(QMainWindow):
    """Main window for the application."""
    def __init__(self, width: int, height: int):
        super().__init__()
        self.setWindowTitle("Minecraft Landscape Generator")

        self.landscape_widget = LandscapeWidget(width, height)
        self.width = width
        self.height = height
        self.scale = 10.0
        self.octaves = 6
        self.persistence = 0.5
        self.lacunarity = 2.0
        self.tree_density = 0.1
        self.water_level = 0.3
        self.cloud_density = 0.2
        self.animation_speed = 50

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_landscape)
        self.animation_running = False
        self.animation_step = 0

        self.init_ui()
        self.generate_and_display()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Left side: Landscape display
        main_layout.addWidget(self.landscape_widget)

        # Right side: Controls
        controls_layout = QVBoxLayout()

        # Sliders
        self.scale_slider = self.create_slider(1, 50, int(self.scale), "Scale")
        self.octaves_slider = self.create_slider(1, 10, self.octaves, "Octaves")
        self.persistence_slider = self.create_slider(1, 100, int(self.persistence * 100), "Persistence")
        self.lacunarity_slider = self.create_slider(1, 100, int(self.lacunarity * 100), "Lacunarity")
        self.tree_density_slider = self.create_slider(0, 100, int(self.tree_density * 100), "Tree Density")
        self.water_level_slider = self.create_slider(0, 100, int(self.water_level * 100), "Water Level")
        self.cloud_density_slider = self.create_slider(0, 100, int(self.cloud_density * 100), "Cloud Density")

        controls_layout.addWidget(self.scale_slider)
        controls_layout.addWidget(self.octaves_slider)
        controls_layout.addWidget(self.persistence_slider)
        controls_layout.addWidget(self.lacunarity_slider)
        controls_layout.addWidget(self.tree_density_slider)
        controls_layout.addWidget(self.water_level_slider)
        controls_layout.addWidget(self.cloud_density_slider)

        # Animation Speed
        animation_speed_layout = QHBoxLayout()
        animation_speed_label = QLabel("Animation Speed:")
        self.animation_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.animation_speed_slider.setRange(1, 100)
        self.animation_speed_slider.setValue(self.animation_speed)
        self.animation_speed_slider.valueChanged.connect(self.update_animation_speed)
        animation_speed_layout.addWidget(animation_speed_label)
        animation_speed_layout.addWidget(self.animation_speed_slider)
        controls_layout.addLayout(animation_speed_layout)

        # Buttons
        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.generate_and_display)
        controls_layout.addWidget(self.generate_button)

        self.animate_button = QPushButton("Animate")
        self.animate_button.clicked.connect(self.toggle_animation)
        controls_layout.addWidget(self.animate_button)

        # Save to File Button
        self.save_button = QPushButton("Save to File")
        self.save_button.clicked.connect(self.save_to_file)
        controls_layout.addWidget(self.save_button)

        # Create World Button
        self.create_world_button = QPushButton("Create World")
        self.create_world_button.clicked.connect(self.create_and_log_world)
        controls_layout.addWidget(self.create_world_button)

        main_layout.addLayout(controls_layout)

        self.show()

    def create_slider(self, min_val: int, max_val: int, default_val: int, label_text: str) -> QWidget:
        """Creates a slider with a label."""
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default_val)
        slider.valueChanged.connect(self.update_parameters)

        label = QLabel(label_text)
        value_label = QLabel(str(default_val))
        slider.valueChanged.connect(lambda value, lbl=value_label: lbl.setText(str(value)))

        layout = QVBoxLayout()
        layout.addWidget(label)
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(slider)
        slider_layout.addWidget(value_label)
        layout.addLayout(slider_layout)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def update_parameters(self):
        """Updates the landscape parameters based on slider values."""
        self.scale = self.scale_slider.value()
        self.octaves = self.octaves_slider.value()
        self.persistence = self.persistence_slider.value() / 100.0
        self.lacunarity = self.lacunarity_slider.value() / 100.0
        self.tree_density = self.tree_density_slider.value() / 100.0
        self.water_level = self.water_level_slider.value() / 100.0
        self.cloud_density = self.cloud_density_slider.value() / 100.0
        self.generate_and_display()

    def generate_and_display(self):
        """Generates a new landscape and displays it."""
        try:
            landscape = generate_landscape(self.width, self.height, self.scale, self.octaves,
                                           self.persistence, self.lacunarity)
            landscape = add_trees(landscape, self.tree_density)
            landscape = add_water(landscape, self.water_level)
            landscape = add_clouds(landscape, self.cloud_density)
            self.landscape_widget.set_landscape(landscape)
        except Exception as e:
            logging.error(f"Error generating landscape: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while generating the landscape:\n{e}")

    def animate_landscape(self):
        """Animates the landscape by varying parameters over time."""
        try:
            self.animation_step += 1
            scale = 10.0 + self.animation_step * 0.5
            landscape = generate_landscape(self.width, self.height, scale)
            landscape = add_trees(landscape, self.tree_density)
            landscape = add_water(landscape, self.water_level)
            landscape = add_clouds(landscape, self.cloud_density)
            self.landscape_widget.set_landscape(landscape)
        except Exception as e:
            logging.error(f"Error during animation: {e}")
            self.timer.stop()
            self.animation_running = False
            self.animate_button.setText("Animate")
            QMessageBox.critical(self, "Error", f"An error occurred during animation:\n{e}")

    def toggle_animation(self):
        """Starts or stops the animation."""
        if self.animation_running:
            self.timer.stop()
            self.animation_running = False
            self.animate_button.setText("Animate")
        else:
            self.animation_step = 0
            self.timer.start(self.animation_speed)  # Adjust the interval as needed
            self.animation_running = True
            self.animate_button.setText("Stop Animation")

    def update_animation_speed(self):
        """Updates the animation speed based on slider value."""
        self.animation_speed = self.animation_speed_slider.value()
        if self.animation_running:
            self.timer.setInterval(self.animation_speed)

    def save_to_file(self):
        """Saves the current landscape image to a file."""
        options = QFileDialog.Options()
        options |= QFileDialog.Option.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;All Files (*)",
                                                   options=options)
        if file_name:
            if not file_name.endswith(".png"):
                file_name += ".png"
            if self.landscape_widget.image.save(file_name, "PNG"):
                QMessageBox.information(self, "Success", f"Image saved to {file_name}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save image.")

    def create_and_log_world(self):
        """Creates a Minecraft world with biomes, blocks, and entities, and logs its state."""
        try:
            # Create some blocks
            blocks = [
                create_block(0, 0, 0, BlockType.GRASS),
                create_block(0, 1, 0, BlockType.DIRT),
                create_block(0, 2, 0, BlockType.STONE),
                create_block(1, 0, 0, BlockType.SAND),
                create_block(1, 1, 0, BlockType.SAND),
                create_block(1, 2, 0, BlockType.SAND),
                create_block(1, 2, 1, BlockType.GOLD_ORE)
            ]

            # Create some entities
            entities = [
                create_entity(5, 0, 5, EntityType.PLAYER, 100),
                create_entity(10, 0, 10, EntityType.CREEPER, 20),
                create_entity(15, 0, 15, EntityType.ZOMBIE, 30),
                create_entity(8, 3, 2, EntityType.VILLAGER, 4)
            ]

            # Create a biome
            plains_biome = create_biome("Sunny Plains", BiomeType.PLAINS, blocks, entities)

            # Create another biome with different blocks and entities
            desert_blocks = [
                create_block(0, 0, 0, BlockType.SAND),
                create_block(0, 1, 0, BlockType.SAND),
                create_block(0, 2, 0, BlockType.SAND),
                create_block(1, 2, 1, BlockType.DIAMOND_ORE)
            ]
            desert_entities = [
                create_entity(5, 0, 5, EntityType.SKELETON, 25),
                create_entity(10, 0, 10, EntityType.SPIDER, 15),
            ]
            desert_biome = create_biome("Arid Desert", BiomeType.DESERT, desert_blocks, desert_entities)

            # Create a world with the biomes
            my_world = create_world("My Awesome World", [plains_biome, desert_biome])

            # Add a new biome to the world
            forest_blocks = [
                create_block(0, 0, 0, BlockType.GRASS),
                create_block(0, 1, 0, BlockType.DIRT),
                create_block(0, 2, 0, BlockType.WOOD),
                create_block(0, 3, 0, BlockType.LEAVES),
            ]
            forest_entities = [
                create_entity(5, 0, 5, EntityType.ENDERMAN, 40),
                create_entity(10, 0, 10, EntityType.VILLAGER, 20),
            ]
            forest_biome = create_biome("Dense Forest", BiomeType.FOREST, forest_blocks, forest_entities)
            my_world.biomes.append(forest_biome)

            # Update the world time
            my_world.time = 18000  # Set to night

            # Change the weather
            my_world.weather = "rain"

            # Log the world state
            log_message = f"World: {my_world.name}, Time: {my_world.time}, Weather: {my_world.weather}\n"
            for biome in my_world.biomes:
                log_message += f"  Biome: {biome.name}, Type: {biome.type}\n"
                for block in biome.blocks:
                    log_message += f"    Block at ({block.x}, {block.y}, {block.z}): {block.type}\n"
                for entity in biome.entities:
                    log_message += f"    Entity at ({entity.x}, {entity.y}, {entity.z}): {entity.type}, Health: {entity.health}\n"

            logging.info(log_message)
            QMessageBox.information(self, "World Created", "Minecraft world created and logged successfully.")

        except Exception as e:
            logging.error(f"Error creating world: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while creating the world:\n{e}")

def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    window = MainWindow(800, 600)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
