"""
Landscape Widget Module

This module defines the LandscapeWidget class, a custom QWidget for rendering 
and interacting with the Minecraft landscape in the Winchester's Minecraft 
World Generator application. It handles the display of the generated landscape, 
user interactions like panning and zooming, and provides visual feedback for 
selected blocks and entities. The widget uses PyQt6 for rendering and event 
handling.

Classes:
    LandscapeWidget: A QWidget subclass for rendering and interacting with the Minecraft landscape.
"""
from typing import List, Dict, Any
from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox
from PyQt6.QtGui import QImage, QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QTimer
import logging
from core.biome import BiomeType

class LandscapeWidget(QWidget):
    """Widget for rendering the Minecraft landscape and handling user interactions."""

    def __init__(self, width: int, height: int):
        """
        Initializes the LandscapeWidget with a given width and height.

        Args:
            width (int): The width of the widget.
            height (int): The height of the widget.
        """
        super().__init__()
        self.width = width
        self.height = height
        self.landscape = None
        self.image = QImage(self.width, self.height, QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white)
        self.zoom_level = 1.0
        self.pan_offset = (0, 0)
        self.last_mouse_pos = None
        self.selected_block = None
        self.selected_entity = None
        self.biome_info = None
        self.hover_info = None

        self.init_ui()

    def init_ui(self):
        """Initializes the UI components of the widget."""
        self.setMinimumSize(self.width, self.height)
        self.setMouseTracking(True)  # Enable mouse tracking for hover events

    def set_landscape(self, landscape: List[List[Dict[str, Any]]]):
        """
        Sets the landscape data for the widget to render.

        Args:
            landscape (List[List[Dict[str, Any]]]): The landscape data.
        """
        self.landscape = landscape
        self.update_image()
        self.update()

    def update_image(self):
        """Updates the image to be rendered based on the current landscape data."""
        if self.landscape is None:
            return

        block_size = 5 * self.zoom_level
        base_offset_x = (
            (self.width - len(self.landscape[0]) * block_size) / 2 + self.pan_offset[0]
        )
        base_offset_y = (
            (self.height - len(self.landscape) * block_size) / 2 + self.pan_offset[1]
        )

        painter = QPainter(self.image)
        painter.fillRect(self.image.rect(), Qt.GlobalColor.white)

        for y in range(len(self.landscape)):
            for x in range(len(self.landscape[0])):
                data = self.landscape[y][x]
                height_value = data["height"]
                biome_type = data["biome"]
                feature = data.get("feature")

                block_x = int(base_offset_x + x * block_size)
                block_y = int(base_offset_y + y * block_size)

                if 0 <= block_x < self.width and 0 <= block_y < self.height:
                    if feature == "tree":
                        color = QColor("darkgreen")
                    elif feature == "water":
                        color = QColor("blue")
                    elif feature == "cloud":
                        color = QColor("lightblue")
                    else:
                        if biome_type == BiomeType.PLAINS:
                            color = QColor("lightgreen")
                        elif biome_type == BiomeType.FOREST:
                            color = QColor("green")
                        elif biome_type == BiomeType.DESERT:
                            color = QColor("yellow")
                        elif biome_type == BiomeType.OCEAN:
                            color = QColor("darkblue")
                        elif biome_type == BiomeType.MOUNTAIN:
                            color = QColor("gray")
                        else:
                            color = QColor("white")
                        shade = int(height_value * 255)
                        color = QColor(shade, shade, shade)

                    painter.fillRect(
                        QRect(block_x, block_y, int(block_size), int(block_size)), color
                    )

        painter.end()

    def paintEvent(self, event):
        """
        Handles the paint event for the widget.

        Args:
            event (QPaintEvent): The paint event.
        """
        painter = QPainter(self)
        painter.drawImage(self.rect(), self.image)

        if self.selected_block:
            block_size = 5 * self.zoom_level
            base_offset_x = (
                (self.width - len(self.landscape[0]) * block_size) / 2
                + self.pan_offset[0]
            )
            base_offset_y = (
                (self.height - len(self.landscape) * block_size) / 2
                + self.pan_offset[1]
            )
            block_x = int(base_offset_x + self.selected_block[0] * block_size)
            block_y = int(base_offset_y + self.selected_block[1] * block_size)
            painter.setPen(QPen(Qt.GlobalColor.red, 2))
            painter.drawRect(block_x, block_y, int(block_size), int(block_size))

        if self.hover_info:
            info_text = f"Biome: {self.hover_info['biome'].value}\nHeight: {self.hover_info['height']:.2f}"
            if "feature" in self.hover_info:
                info_text += f"\nFeature: {self.hover_info['feature']}"
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(10, 20, info_text)

    def mousePressEvent(self, event):
        """
        Handles the mouse press event for the widget.

        Args:
            event (QMouseEvent): The mouse event.
        """
        self.last_mouse_pos = event.pos()

        block_size = 5 * self.zoom_level
        base_offset_x = (
            (self.width - len(self.landscape[0]) * block_size) / 2 + self.pan_offset[0]
        )
        base_offset_y = (
            (self.height - len(self.landscape) * block_size) / 2 + self.pan_offset[1]
        )
        x = int((event.pos().x() - base_offset_x) / block_size)
        y = int((event.pos().y() - base_offset_y) / block_size)

        if self.landscape and 0 <= x < len(self.landscape[0]) and 0 <= y < len(self.landscape):
            self.selected_block = (x, y)
            self.biome_info = self.landscape[y][x]["biome"].value  # Get the biome value
            self.update()
        else:
            self.selected_block = None
            self.biome_info = None
            self.update()

    def mouseMoveEvent(self, event):
        """
        Handles the mouse move event for the widget.

        Args:
            event (QMouseEvent): The mouse event.
        """
        if self.last_mouse_pos:
            dx = event.pos().x() - self.last_mouse_pos.x()
            dy = event.pos().y() - self.last_mouse_pos.y()
            self.pan_offset = (self.pan_offset[0] + dx, self.pan_offset[1] + dy)
            self.last_mouse_pos = event.pos()
            self.update_image()
            self.update()

        block_size = 5 * self.zoom_level
        base_offset_x = (
            (self.width - len(self.landscape[0]) * block_size) / 2 + self.pan_offset[0]
        )
        base_offset_y = (
            (self.height - len(self.landscape) * block_size) / 2 + self.pan_offset[1]
        )
        x = int((event.pos().x() - base_offset_x) / block_size)
        y = int((event.pos().y() - base_offset_y) / block_size)

        if self.landscape and 0 <= x < len(self.landscape[0]) and 0 <= y < len(self.landscape):
            self.hover_info = self.landscape[y][x]
            self.update()
        else:
            self.hover_info = None
            self.update()

    def mouseReleaseEvent(self, event):
        """
        Handles the mouse release event for the widget.

        Args:
            event (QMouseEvent): The mouse event.
        """
        self.last_mouse_pos = None

    def wheelEvent(self, event):
        """
        Handles the mouse wheel event for the widget.

        Args:
            event (QWheelEvent): The wheel event.
        """
        zoom_in = event.angleDelta().y() > 0
        if zoom_in:
            self.zoom_level = min(self.zoom_level + 0.1, 5.0)
        else:
            self.zoom_level = max(self.zoom_level - 0.1, 0.2)
        self.update_image()
        self.update()

    def reset_view(self):
        """Resets the zoom level and panning to default."""
        self.zoom_level = 1.0
        self.pan_offset = (0, 0)
        self.update_image()
        self.update()
