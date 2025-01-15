import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.logger import get_logger

# Set up the logger for the main application
logger = get_logger("main")

def main():
    """
    Main function to run the Minecraft World Generator application.
    """
    logger.info("Starting the Minecraft World Generator application")

    # Create the application instance
    app = QApplication(sys.argv)

    # Create the main window with specified dimensions
    window = MainWindow(800, 600)

    # Show the main window
    window.show()

    # Start the application event loop
    exit_code = app.exec()

    logger.info("Exiting the application with code %d", exit_code)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()