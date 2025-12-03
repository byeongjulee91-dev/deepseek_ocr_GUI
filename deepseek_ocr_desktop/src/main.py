"""
DeepSeek-OCR Desktop Application
Entry point for the PySide6 desktop GUI application
"""

import sys
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import Qt

# Import application components
from .core.model_manager import ModelManager
from .ui.main_window import MainWindow
from .ui.dialogs.model_loading_dialog import ModelLoadingDialog
from .utils.config import AppConfig
from .utils.logger import setup_logger, get_logger

# Initialize logger
logger = setup_logger("DeepSeekOCR", level=10)  # DEBUG level
app_logger = get_logger(__name__)


def main():
    """Main entry point for the application"""
    app_logger.info("="*60)
    app_logger.info("DeepSeek-OCR Desktop Application Starting")
    app_logger.info("="*60)

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("DeepSeek-OCR Desktop")
    app.setOrganizationName("DeepSeekOCR")
    app.setOrganizationDomain("deepseek.ai")
    app_logger.info("Qt Application created")

    # Enable high DPI scaling
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app_logger.debug("High DPI scaling enabled")

    # Load application stylesheet
    import os
    qss_path = os.path.join(os.path.dirname(__file__), "resources", "styles", "app.qss")
    if os.path.exists(qss_path):
        with open(qss_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
        app_logger.info(f"Stylesheet loaded from: {qss_path}")
    else:
        app_logger.warning(f"Stylesheet not found: {qss_path}")

    # Load configuration
    config = AppConfig()
    model_name = config.get_model_name()
    hf_home = config.get_hf_home()

    # Load vLLM configuration
    use_vllm = config.get_use_vllm()
    vllm_endpoint = config.get_vllm_endpoint()
    vllm_api_key = config.get_vllm_api_key()

    if use_vllm:
        app_logger.info(f"Configuration loaded - Mode: vLLM, Endpoint: {vllm_endpoint}, Model: {model_name}")
    else:
        app_logger.info(f"Configuration loaded - Mode: Local, Model: {model_name}, HF_HOME: {hf_home}")

    # Create model manager
    app_logger.info("Creating model manager...")
    model_manager = ModelManager()

    # Create and show loading dialog
    app_logger.debug("Creating loading dialog...")
    loading_dialog = ModelLoadingDialog()

    # Connect model manager signals to loading dialog
    model_manager.load_progress_signal.connect(loading_dialog.update_progress)
    model_manager.load_error_signal.connect(loading_dialog.show_error)
    app_logger.debug("Model manager signals connected")

    # Reference to main window (will be created after model loads)
    main_window = None

    def on_model_loaded(model, tokenizer):
        """Called when model is loaded successfully"""
        nonlocal main_window

        app_logger.info("Model loaded successfully!")

        # Close loading dialog
        loading_dialog.model_loaded()

        # Create and show main window
        app_logger.info("Creating main window...")
        main_window = MainWindow(model_manager, config)
        main_window.show()
        app_logger.info("Main window displayed")

    # Connect model loaded signal
    model_manager.model_loaded_signal.connect(on_model_loaded)

    # Start loading model or connecting to vLLM
    if use_vllm:
        app_logger.info(f"Connecting to vLLM endpoint: {vllm_endpoint}")
        model_manager.load_model_async(
            model_name,
            hf_home,
            use_vllm=True,
            vllm_endpoint=vllm_endpoint,
            vllm_api_key=vllm_api_key
        )
    else:
        app_logger.info(f"Starting local model loading: {model_name}")
        model_manager.load_model_async(model_name, hf_home)

    # Show loading dialog (blocks until model loads or error)
    app_logger.debug("Showing loading dialog...")
    result = loading_dialog.exec()

    # If loading was canceled or failed, exit
    if result == QDialog.DialogCode.Rejected:
        app_logger.warning("Model loading cancelled or failed")
        return 0

    # Start Qt event loop
    app_logger.info("Starting Qt event loop...")
    return_code = app.exec()
    app_logger.info(f"Application exited with code: {return_code}")
    return return_code


if __name__ == "__main__":
    # This file should not be run directly
    # Use run.py from the project root instead
    print("❌ Error: Do not run main.py directly!")
    print("✅ Use: python run.py from the project root directory")
    print("   Or: uv run run.py")
    sys.exit(1)
