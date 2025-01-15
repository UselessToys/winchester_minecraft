from typing import List, Dict, Any
from PyQt6.QtWidgets import QWidget, QApplication, QMessageBox
from PyQt6.QtGui import QImage, QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QTimer
import logging

class LandscapeWidget(QWidget):
    """Widget for rendering the Minecraft landscape and handling user interactions."""

    def __init__(self, width: int, height: int):
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
        self.setMinimumSize(self.width, self.height)
        self.setMouseTracking(True)  # Enable mouse tracking for hover events

    def set_landscape(self, landscape: List[List[Dict[str, Any]]]):
        self.landscape = landscape
        self.update_image()
        self.update()

    def update_image(self):
        if self.landscape is None:
            return

        block_size = 5 * self.zoom_level
        base_offset_x = (
            (self.width - len(self.landscape[0]) * block_size) / 2 + self.pan_offset[0]
        )
        base_offset_y = (
            (self.height - len(self.landscape) * block_size) / 2 + self.pan_offset[1]
        )

        for y in range(self.height):
            for x in range(self.width):
                self.image.setPixelColor(x, y, QColor("white"))

        for y in range(len(self.landscape)):
            for x in range(len(self.landscape[0])):
                data = self.landscape[y][x]
                height_value = data["height"]
                biome_type = data["biome"]
                feature = data.get("feature")

                # Calculate block position based on zoom and pan
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
                        # Terrain shading
                        shade = int(height_value * 255)
                        color = QColor(shade, shade, shade)

                    for px in range(int(block_size)):
                        for py in range(int(block_size)):
                            if (
                                0 <= block_x + px < self.width
                                and 0 <= block_y + py < self.height
                            ):
                                self.image.setPixelColor(
                                    int(block_x + px), int(block_y + py), color
                                )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(self.rect(), self.image)

        # Draw selected block highlight
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

        # Display hover info
        if self.hover_info:
            info_text = f"Biome: {self.hover_info['biome'].value}\nHeight: {self.hover_info['height']:.2f}"
            if "feature" in self.hover_info:
                info_text += f"\nFeature: {self.hover_info['feature']}"
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(10, 20, info_text)

    def mousePressEvent(self, event):
        self.last_mouse_pos = event.pos()

        # Convert mouse position to landscape coordinates
        block_size = 5 * self.zoom_level
        base_offset_x = (
            (self.width - len(self.landscape[0]) * block_size) / 2 + self.pan_offset[0]
        )
        base_offset_y = (
            (self.height - len(self.landscape) * block_size) / 2 + self.pan_offset[1]
        )
        x = int((event.pos().x() - base_offset_x) / block_size)
        y = int((event.pos().y() - base_offset_y) / block_size)

        if 0 <= x < len(self.landscape[0]) and 0 <= y < len(self.landscape):
            self.selected_block = (x, y)
            self.biome_info = self.landscape[y][x]["biome"]
            self.update()
        else:
            self.selected_block = None
            self.biome_info = None
            self.update()

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos:
            dx = event.pos().x() - self.last_mouse_pos.x()
            dy = event.pos().y() - self.last_mouse_pos.y()
            self.pan_offset = (self.pan_offset[0] + dx, self.pan_offset[1] + dy)
            self.last_mouse_pos = event.pos()
            self.update_image()
            self.update()

        # Convert mouse position to landscape coordinates
        block_size = 5 * self.zoom_level
        base_offset_x = (
            (self.width - len(self.landscape[0]) * block_size) / 2 + self.pan_offset[0]
        )
        base_offset_y = (
            (self.height - len(self.landscape) * block_size) / 2 + self.pan_offset[1]
        )
        x = int((event.pos().x() - base_offset_x) / block_size)
        y = int((event.pos().y() - base_offset_y) / block_size)

        if 0 <= x < len(self.landscape[0]) and 0 <= y < len(self.landscape):
            self.hover_info = self.landscape[y][x]
            self.update()
        else:
            self.hover_info = None
            self.update()

    def mouseReleaseEvent(self, event):
        self.last_mouse_pos = None

    def wheelEvent(self, event):
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
