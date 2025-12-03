"""
Settings Dialog
Comprehensive settings dialog for all application settings
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QLineEdit, QSpinBox, QCheckBox,
    QPushButton, QFormLayout, QGroupBox, QFileDialog,
    QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont


class SettingsDialog(QDialog):
    """Dialog for editing application settings"""

    def __init__(self, config, parent=None):
        """Initialize settings dialog

        Args:
            config: AppConfig instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("Settings - DeepSeek OCR Desktop")
        self.setMinimumSize(QSize(600, 500))

        layout = QVBoxLayout()

        # Title
        title = QLabel("⚙️ Application Settings")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 10px; color: #0ea5e9;")
        layout.addWidget(title)

        # Tab widget
        self.tab_widget = QTabWidget()

        # Model settings tab
        self.model_tab = self.create_model_tab()
        self.tab_widget.addTab(self.model_tab, "🤖 Model")

        # Processing settings tab
        self.processing_tab = self.create_processing_tab()
        self.tab_widget.addTab(self.processing_tab, "⚡ Processing")

        # PDF settings tab
        self.pdf_tab = self.create_pdf_tab()
        self.tab_widget.addTab(self.pdf_tab, "📄 PDF")

        # UI settings tab
        self.ui_tab = self.create_ui_tab()
        self.tab_widget.addTab(self.ui_tab, "🎨 Interface")

        layout.addWidget(self.tab_widget)

        # Buttons
        button_layout = QHBoxLayout()

        self.reset_button = QPushButton("🔄 Reset All")
        self.reset_button.clicked.connect(self.reset_all)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        button_layout.addWidget(self.reset_button)

        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("💾 Save")
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def create_model_tab(self) -> QWidget:
        """Create model settings tab

        Returns:
            Model settings widget
        """
        tab = QWidget()
        layout = QVBoxLayout()

        # Model group
        model_group = QGroupBox("Model Configuration")
        model_layout = QFormLayout()

        self.model_name_edit = QLineEdit()
        self.model_name_edit.setPlaceholderText("deepseek-ai/DeepSeek-OCR")
        self.model_name_edit.setToolTip("HuggingFace model name")
        model_layout.addRow("Model Name:", self.model_name_edit)

        self.hf_home_edit = QLineEdit()
        self.hf_home_edit.setPlaceholderText("~/.cache/huggingface")
        self.hf_home_edit.setToolTip("HuggingFace cache directory")

        hf_home_row = QHBoxLayout()
        hf_home_row.addWidget(self.hf_home_edit)

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_hf_home)
        hf_home_row.addWidget(browse_button)

        model_layout.addRow("HF Cache:", hf_home_row)

        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        # Info
        info = QLabel(
            "⚠️ Changing model settings requires restarting the application.\n"
            "Model will be downloaded on next startup if not cached."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #f59e0b; padding: 10px; background-color: rgba(245, 158, 11, 0.1); border-radius: 6px;")
        layout.addWidget(info)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def create_processing_tab(self) -> QWidget:
        """Create processing settings tab

        Returns:
            Processing settings widget
        """
        tab = QWidget()
        layout = QVBoxLayout()

        # Image processing group
        img_group = QGroupBox("Image Processing")
        img_layout = QFormLayout()

        self.base_size_spin = QSpinBox()
        self.base_size_spin.setMinimum(512)
        self.base_size_spin.setMaximum(2048)
        self.base_size_spin.setSingleStep(128)
        self.base_size_spin.setToolTip("Base size for image processing (higher = better quality, slower)")
        img_layout.addRow("Base Size:", self.base_size_spin)

        self.image_size_spin = QSpinBox()
        self.image_size_spin.setMinimum(320)
        self.image_size_spin.setMaximum(1280)
        self.image_size_spin.setSingleStep(64)
        self.image_size_spin.setToolTip("Image size for model input")
        img_layout.addRow("Image Size:", self.image_size_spin)

        img_group.setLayout(img_layout)
        layout.addWidget(img_group)

        # Processing options group
        options_group = QGroupBox("Processing Options")
        options_layout = QVBoxLayout()

        self.crop_mode_check = QCheckBox("Enable crop mode")
        self.crop_mode_check.setToolTip("Crop image to focus area (recommended)")
        options_layout.addWidget(self.crop_mode_check)

        self.test_compress_check = QCheckBox("Test compression")
        self.test_compress_check.setToolTip("Test different compression levels (slower but may improve quality)")
        options_layout.addWidget(self.test_compress_check)

        self.include_caption_check = QCheckBox("Include image captions")
        self.include_caption_check.setToolTip("Generate image captions in PDF processing")
        options_layout.addWidget(self.include_caption_check)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def create_pdf_tab(self) -> QWidget:
        """Create PDF settings tab

        Returns:
            PDF settings widget
        """
        tab = QWidget()
        layout = QVBoxLayout()

        # PDF processing group
        pdf_group = QGroupBox("PDF Processing")
        pdf_layout = QFormLayout()

        self.pdf_dpi_spin = QSpinBox()
        self.pdf_dpi_spin.setMinimum(72)
        self.pdf_dpi_spin.setMaximum(300)
        self.pdf_dpi_spin.setSingleStep(12)
        self.pdf_dpi_spin.setSuffix(" DPI")
        self.pdf_dpi_spin.setToolTip("DPI for PDF to image conversion (higher = better quality, larger file)")
        pdf_layout.addRow("Default DPI:", self.pdf_dpi_spin)

        pdf_group.setLayout(pdf_layout)
        layout.addWidget(pdf_group)

        # PDF options group
        pdf_options_group = QGroupBox("PDF Options")
        pdf_options_layout = QVBoxLayout()

        self.extract_images_check = QCheckBox("Extract embedded images by default")
        self.extract_images_check.setToolTip("Extract and save images found in PDFs")
        pdf_options_layout.addWidget(self.extract_images_check)

        pdf_options_group.setLayout(pdf_options_layout)
        layout.addWidget(pdf_options_group)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def create_ui_tab(self) -> QWidget:
        """Create UI settings tab

        Returns:
            UI settings widget
        """
        tab = QWidget()
        layout = QVBoxLayout()

        # Window group
        window_group = QGroupBox("Window Settings")
        window_layout = QVBoxLayout()

        self.restore_geometry_check = QCheckBox("Remember window size and position")
        self.restore_geometry_check.setToolTip("Restore window geometry on startup")
        window_layout.addWidget(self.restore_geometry_check)

        self.restore_splitter_check = QCheckBox("Remember panel sizes")
        self.restore_splitter_check.setToolTip("Restore splitter state on startup")
        window_layout.addWidget(self.restore_splitter_check)

        window_group.setLayout(window_layout)
        layout.addWidget(window_group)

        # Clear cache button
        clear_cache_button = QPushButton("🗑️ Clear Window State")
        clear_cache_button.setToolTip("Clear saved window geometry and state")
        clear_cache_button.clicked.connect(self.clear_window_state)
        clear_cache_button.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        layout.addWidget(clear_cache_button)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def load_settings(self):
        """Load current settings from config"""
        # Model settings
        self.model_name_edit.setText(self.config.get_model_name())
        self.hf_home_edit.setText(self.config.get_hf_home())

        # Processing settings
        self.base_size_spin.setValue(self.config.get_base_size())
        self.image_size_spin.setValue(self.config.get_image_size())
        self.crop_mode_check.setChecked(self.config.get_crop_mode())
        self.test_compress_check.setChecked(self.config.get_test_compress())
        self.include_caption_check.setChecked(self.config.get_include_caption())

        # PDF settings
        self.pdf_dpi_spin.setValue(self.config.get_pdf_dpi())
        self.extract_images_check.setChecked(self.config.get_pdf_extract_images())

        # UI settings
        self.restore_geometry_check.setChecked(True)  # Always enabled for now
        self.restore_splitter_check.setChecked(True)

    def browse_hf_home(self):
        """Browse for HuggingFace cache directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select HuggingFace Cache Directory",
            self.hf_home_edit.text() or "~/.cache/huggingface"
        )

        if directory:
            self.hf_home_edit.setText(directory)

    def clear_window_state(self):
        """Clear saved window state"""
        reply = QMessageBox.question(
            self,
            "Clear Window State",
            "This will clear saved window size, position, and panel sizes.\n\n"
            "The window will reset to default layout on next startup.\n\n"
            "Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.config.settings.remove("window/geometry")
            self.config.settings.remove("window/state")
            self.config.settings.remove("window/splitter_state")
            self.config.sync()

            QMessageBox.information(
                self,
                "Cleared",
                "Window state has been cleared!"
            )

    def save_settings(self):
        """Save settings to config"""
        # Model settings
        self.config.set_model_name(self.model_name_edit.text())
        self.config.set_hf_home(self.hf_home_edit.text())

        # Processing settings
        self.config.set_base_size(self.base_size_spin.value())
        self.config.set_image_size(self.image_size_spin.value())
        self.config.set_crop_mode(self.crop_mode_check.isChecked())
        self.config.set_test_compress(self.test_compress_check.isChecked())
        self.config.set_include_caption(self.include_caption_check.isChecked())

        # PDF settings
        self.config.set_pdf_dpi(self.pdf_dpi_spin.value())
        self.config.set_pdf_extract_images(self.extract_images_check.isChecked())

        # Sync to disk
        self.config.sync()

        # Show success message
        QMessageBox.information(
            self,
            "Settings Saved",
            "Settings have been saved successfully!\n\n"
            "Note: Some changes may require restarting the application."
        )

        self.accept()

    def reset_all(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.warning(
            self,
            "Reset All Settings",
            "This will reset ALL settings to their default values.\n\n"
            "This action cannot be undone.\n\n"
            "Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Reset to defaults
            self.model_name_edit.setText("deepseek-ai/DeepSeek-OCR")
            self.hf_home_edit.setText("~/.cache/huggingface")
            self.base_size_spin.setValue(1024)
            self.image_size_spin.setValue(640)
            self.crop_mode_check.setChecked(True)
            self.test_compress_check.setChecked(False)
            self.include_caption_check.setChecked(False)
            self.pdf_dpi_spin.setValue(144)
            self.extract_images_check.setChecked(True)

            QMessageBox.information(
                self,
                "Reset Complete",
                "All settings have been reset to defaults.\n\n"
                "Click 'Save' to apply the changes."
            )
