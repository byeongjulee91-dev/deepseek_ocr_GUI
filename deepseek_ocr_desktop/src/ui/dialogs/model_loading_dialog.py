"""
Model Loading Dialog
Modal progress dialog shown during model loading
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar,
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class ModelLoadingDialog(QDialog):
    """Modal dialog to display model loading progress"""

    def __init__(self, parent=None):
        """Initialize loading dialog

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setup_ui()
        self.setModal(True)

    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("Loading DeepSeek-OCR Model")
        self.setMinimumWidth(500)
        self.setMinimumHeight(200)

        # Create layout
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Title label
        title_label = QLabel("🚀 Initializing DeepSeek-OCR")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Progress bar (indeterminate)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Indeterminate mode
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Preparing to load model...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Info label
        info_label = QLabel(
            "⏳ This may take 10-30 seconds depending on your system.\n"
            "The model (~5-10GB) will be loaded into GPU memory."
        )
        info_label.setStyleSheet("color: gray;")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Cancel button (initially hidden)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setVisible(False)  # Optional: add cancel functionality
        layout.addWidget(self.cancel_button)

        layout.addStretch()
        self.setLayout(layout)

    def update_progress(self, message: str):
        """Update progress message

        Args:
            message: Progress message to display
        """
        self.status_label.setText(message)

    def show_error(self, error_message: str):
        """Show error message and close dialog

        Args:
            error_message: Error message to display
        """
        QMessageBox.critical(
            self,
            "Model Loading Error",
            f"Failed to load model:\n\n{error_message}\n\n"
            "Please check:\n"
            "• CUDA is properly installed\n"
            "• You have an NVIDIA GPU with 8GB+ VRAM\n"
            "• You have sufficient disk space (~10GB)\n"
            "• Internet connection is available for model download",
        )
        self.reject()

    def model_loaded(self):
        """Called when model loading is complete"""
        self.status_label.setText("✅ Model loaded successfully!")
        self.accept()
