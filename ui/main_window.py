from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSlider, QLabel, QTextEdit, QGridLayout, QScrollArea, QGroupBox, QComboBox
from PyQt6 import uic
from PyQt6.QtCore import QTimer, Qt
from .landscape_widget import LandscapeWidget
from core.generator import generate_advanced_landscape, add_biome_features
from core.world import World
from core.biome import BiomeType
from core.entity import EntityType
from utils.logger import get_logger

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    """Main window for the application, handling UI elements and interactions."""

    def __init__(self, width: int, height: int):
        super().__init__()
        uic.loadUi("ui/resources/main_window.ui", self)
        self.setWindowTitle("Minecraft World Generator and Explorer")

        self.landscape_widget = LandscapeWidget(width, height)
        self.width = width
        self.height = height
        self.scale = 50.0
        self.octaves = 6
        self.persistence = 0.5
        self.lacunarity = 2.0
        self.tree_density = 0.1
        self.water_level = 0.3
        self.cloud_density = 0.2
        self.animation_speed = 50
        self.biome_scale = 200.0
        self.sea_level = 0.5

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_landscape)
        self.animation_running = False
        self.animation_step = 0
        self.current_world = None

        self.init_ui()
        self.generate_and_display()

    def init_ui(self):
        # Replace the placeholder widget with the actual LandscapeWidget
        central_widget = self.findChild(QWidget, "centralwidget")
        if central_widget:
            layout = central_widget.layout()
            if layout:
                # Remove the placeholder widget
                placeholder_widget = self.findChild(QWidget, "landscapeWidget")
                if placeholder_widget:
                    layout.removeWidget(placeholder_widget)
                    placeholder_widget.deleteLater()

                # Add the actual LandscapeWidget
                layout.insertWidget(0, self.landscape_widget)  # Insert at the correct position

        # Initialize other UI components
        self.init_controls()

        # Connect signals to slots
        self.generate_button.clicked.connect(self.generate_and_display)
        self.reset_view_button.clicked.connect(self.landscape_widget.reset_view)
        self.save_button.clicked.connect(self.save_to_file)
        self.create_world_button.clicked.connect(self.create_and_log_world)
        self.animate_button.clicked.connect(self.toggle_animation)
        self.animation_speed_slider.valueChanged.connect(self.update_animation_speed)

        # Setup text area for sonnet and essay
        self.setup_text_area()

    def init_controls(self):
        """Initializes and connects the control widgets."""
        # --- Sliders Section ---
        self.scale_slider = self.findChild(QSlider, "scaleSlider")
        self.octaves_slider = self.findChild(QSlider, "octavesSlider")
        self.persistence_slider = self.findChild(QSlider, "persistenceSlider")
        self.lacunarity_slider = self.findChild(QSlider, "lacunaritySlider")
        self.tree_density_slider = self.findChild(QSlider, "treeDensitySlider")
        self.water_level_slider = self.findChild(QSlider, "waterLevelSlider")
        self.cloud_density_slider = self.findChild(QSlider, "cloudDensitySlider")
        self.biome_scale_slider = self.findChild(QSlider, "biomeScaleSlider")
        self.sea_level_slider = self.findChild(QSlider, "seaLevelSlider")

        # Set range and default values for sliders
        self.scale_slider.setRange(1, 100)
        self.scale_slider.setValue(int(self.scale))
        self.octaves_slider.setRange(1, 10)
        self.octaves_slider.setValue(self.octaves)
        self.persistence_slider.setRange(1, 100)
        self.persistence_slider.setValue(int(self.persistence * 100))
        self.lacunarity_slider.setRange(1, 100)
        self.lacunarity_slider.setValue(int(self.lacunarity * 100))
        self.tree_density_slider.setRange(0, 100)
        self.tree_density_slider.setValue(int(self.tree_density * 100))
        self.water_level_slider.setRange(0, 100)
        self.water_level_slider.setValue(int(self.water_level * 100))
        self.cloud_density_slider.setRange(0, 100)
        self.cloud_density_slider.setValue(int(self.cloud_density * 100))
        self.biome_scale_slider.setRange(1, 500)
        self.biome_scale_slider.setValue(int(self.biome_scale))
        self.sea_level_slider.setRange(1, 100)
        self.sea_level_slider.setValue(int(self.sea_level * 100))

        # Connect sliders to update parameters
        self.scale_slider.valueChanged.connect(self.update_parameters)
        self.octaves_slider.valueChanged.connect(self.update_parameters)
        self.persistence_slider.valueChanged.connect(self.update_parameters)
        self.lacunarity_slider.valueChanged.connect(self.update_parameters)
        self.tree_density_slider.valueChanged.connect(self.update_parameters)
        self.water_level_slider.valueChanged.connect(self.update_parameters)
        self.cloud_density_slider.valueChanged.connect(self.update_parameters)
        self.biome_scale_slider.valueChanged.connect(self.update_parameters)
        self.sea_level_slider.valueChanged.connect(self.update_parameters)

        # --- Animation Controls ---
        self.animation_speed_slider = self.findChild(QSlider, "animationSpeedSlider")
        self.animate_button = self.findChild(QPushButton, "animateButton")

        # Set range and default value for animation speed slider
        self.animation_speed_slider.setRange(1, 100)
        self.animation_speed_slider.setValue(self.animation_speed)

        # --- Buttons Section ---
        self.generate_button = self.findChild(QPushButton, "generateButton")
        self.reset_view_button = self.findChild(QPushButton, "resetViewButton")
        self.save_button = self.findChild(QPushButton, "saveButton")
        self.create_world_button = self.findChild(QPushButton, "createWorldButton")

        # --- World Display Section ---
        self.world_info_text = self.findChild(QTextEdit, "worldInfoText")

        # --- Biome and Entity Selection ---
        self.biome_combo = self.findChild(QComboBox, "biomeComboBox")
        self.entity_combo = self.findChild(QComboBox, "entityComboBox")

        # Populate biome and entity combo boxes
        self.biome_combo.addItems([biome.value for biome in BiomeType])
        self.entity_combo.addItems([entity.value for entity in EntityType])

    def setup_text_area(self):
        """Sets up the text area for displaying the sonnet and essay."""
        self.text_area = self.findChild(QTextEdit, "textArea")

        # Load and display the sonnet and essay
        self.load_text_content()

    def load_text_content(self):
        """Loads the sonnet and essay into the text area."""
        # Make sure text_area is correctly initialized
        if self.text_area:
            # Set the text of the text area to the sonnet and essay
            self.text_area.setText(f"{sonnet}\n\n{essay}")
        else:
            print("text_area is not initialized.")

    def update_parameters(self):
        """Updates the landscape parameters based on slider values."""
        self.scale = self.scale_slider.value()
        self.octaves = self.octaves_slider.value()
        self.persistence = self.persistence_slider.value() / 100.0
        self.lacunarity = self.lacunarity_slider.value() / 100.0
        self.tree_density = self.tree_density_slider.value() / 100.0
        self.water_level = self.water_level_slider.value() / 100.0
        self.cloud_density = self.cloud_density_slider.value() / 100.0
        self.biome_scale = self.biome_scale_slider.value()
        self.sea_level = self.sea_level_slider.value() / 100.0
        self.generate_and_display()

    def generate_and_display(self):
        """Generates a new landscape and displays it."""
        try:
            landscape = generate_advanced_landscape(
                self.width,
                self.height,
                self.scale,
                self.octaves,
                self.persistence,
                self.lacunarity,
                self.sea_level,
                self.biome_scale,
            )
            landscape = add_biome_features(
                landscape, self.tree_density, self.water_level, self.cloud_density
            )
            self.landscape_widget.set_landscape(landscape)
        except Exception as e:
            logger.error(f"Error generating landscape: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while generating the landscape:\n{e}",
            )

    def animate_landscape(self):
        """Animates the landscape by varying parameters over time."""
        try:
            self.animation_step += 1
            scale = 10.0 + self.animation_step * 0.5
            landscape = generate_advanced_landscape(
                self.width,
                self.height,
                scale,
                self.octaves,
                self.persistence,
                self.lacunarity,
                self.sea_level,
                self.biome_scale,
            )
            landscape = add_biome_features(
                landscape, self.tree_density, self.water_level, self.cloud_density
            )
            self.landscape_widget.set_landscape(landscape)
        except Exception as e:
            logger.error(f"Error during animation: {e}")
            self.timer.stop()
            self.animation_running = False
            self.animate_button.setText("Animate")
            QMessageBox.critical(
                self, "Error", f"An error occurred during animation:\n{e}"
            )

    def toggle_animation(self):
        """Starts or stops the animation."""
        if self.animation_running:
            self.timer.stop()
            self.animation_running = False
            self.animate_button.setText("Animate")
        else:
            self.animation_step = 0
            self.timer.start(self.animation_speed)
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
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "",
            "PNG Files (*.png);;All Files (*)",
            options=options,
        )
        if file_name:
            if not file_name.endswith(".png"):
                file_name += ".png"
            if self.landscape_widget.image.save(file_name, "PNG"):
                QMessageBox.information(
                    self, "Success", f"Image saved to {file_name}"
                )
            else:
                QMessageBox.critical(self, "Error", "Failed to save image.")

    def create_and_log_world(self):
        """Placeholder for creating and logging world data."""
        # Implement world creation and logging logic here
        pass

### Wrapping Up the `ui` Folder

With `main_window.py` and `landscape_widget.py` completed, we now have a fully functional UI for our Minecraft world generator. The `main_window.ui` file, created with Qt Designer, defines the layout, and our Python code brings it to life, connecting it with the backend logic in the `core` folder.

In the next phase, we'll focus on the `utils` folder, where we'll implement a logging utility to keep track of what's happening in our application. We're getting closer to a fully operational Minecraft world generator – keep up the great work!