"""
Advanced Settings Widget
Collapsible panel for OCR processing parameters
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QCheckBox, QGroupBox, QFormLayout,
    QPushButton
)
from PySide6.QtCore import Qt, Signal


class CollapsibleGroupBox(QGroupBox):
    """Group box that can be collapsed/expanded"""

    def __init__(self, title: str, parent=None):
        """Initialize collapsible group box

        Args:
            title: Group box title
            parent: Parent widget
        """
        super().__init__(title, parent)
        self.setCheckable(True)
        self.setChecked(False)  # Start collapsed
        self.toggled.connect(self.on_toggled)

        # Store content widget
        self._content = None

    def setContentWidget(self, widget: QWidget):
        """Set content widget

        Args:
            widget: Content widget
        """
        self._content = widget
        layout = QVBoxLayout()
        layout.addWidget(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)

        # Hide content initially
        widget.setVisible(False)

    def on_toggled(self, checked: bool):
        """Handle toggle state change

        Args:
            checked: Whether group box is checked
        """
        if self._content:
            self._content.setVisible(checked)


class AdvancedSettingsWidget(QWidget):
    """Widget for advanced OCR settings"""

    # Signals emitted when settings change
    settings_changed_signal = Signal(dict)

    def __init__(self, config, parent=None):
        """Initialize advanced settings widget

        Args:
            config: AppConfig instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup widget UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create collapsible group box
        self.group_box = CollapsibleGroupBox("⚙️ Advanced Settings")
        self.group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QGroupBox::indicator {
                width: 13px;
                height: 13px;
            }
            QGroupBox::indicator:unchecked {
                image: url(none);
                border: 2px solid #888;
                background: #333;
            }
            QGroupBox::indicator:checked {
                image: url(none);
                border: 2px solid #0ea5e9;
                background: #0ea5e9;
            }
        """)

        # Content widget
        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Settings form
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)

        # Base size
        self.base_size_spin = QSpinBox()
        self.base_size_spin.setMinimum(512)
        self.base_size_spin.setMaximum(2048)
        self.base_size_spin.setSingleStep(128)
        self.base_size_spin.setValue(1024)
        self.base_size_spin.setToolTip("Base size for image processing (default: 1024)")
        self.base_size_spin.valueChanged.connect(self.on_settings_changed)
        form_layout.addRow("Base Size:", self.base_size_spin)

        # Image size
        self.image_size_spin = QSpinBox()
        self.image_size_spin.setMinimum(320)
        self.image_size_spin.setMaximum(1280)
        self.image_size_spin.setSingleStep(64)
        self.image_size_spin.setValue(640)
        self.image_size_spin.setToolTip("Image size for model input (default: 640)")
        self.image_size_spin.valueChanged.connect(self.on_settings_changed)
        form_layout.addRow("Image Size:", self.image_size_spin)

        # Crop mode
        self.crop_mode_check = QCheckBox("Enable crop mode")
        self.crop_mode_check.setChecked(True)
        self.crop_mode_check.setToolTip("Crop image to focus area (recommended)")
        self.crop_mode_check.stateChanged.connect(self.on_settings_changed)
        form_layout.addRow("", self.crop_mode_check)

        # Test compress
        self.test_compress_check = QCheckBox("Test compression")
        self.test_compress_check.setChecked(False)
        self.test_compress_check.setToolTip("Test different compression levels (slower)")
        self.test_compress_check.stateChanged.connect(self.on_settings_changed)
        form_layout.addRow("", self.test_compress_check)

        # Include caption
        self.include_caption_check = QCheckBox("Include image captions")
        self.include_caption_check.setChecked(False)
        self.include_caption_check.setToolTip("Generate image captions (for PDF processing)")
        self.include_caption_check.stateChanged.connect(self.on_settings_changed)
        form_layout.addRow("", self.include_caption_check)

        content_layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()

        self.reset_button = QPushButton("🔄 Reset to Defaults")
        self.reset_button.setToolTip("Reset all settings to default values")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        button_layout.addWidget(self.reset_button)

        self.save_button = QPushButton("💾 Save as Default")
        self.save_button.setToolTip("Save current settings as default")
        self.save_button.clicked.connect(self.save_as_default)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #0ea5e9;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #0284c7;
            }
        """)
        button_layout.addWidget(self.save_button)

        button_layout.addStretch()
        content_layout.addLayout(button_layout)

        # Info label
        info_label = QLabel("💡 These settings affect OCR accuracy and speed")
        info_label.setStyleSheet("color: gray; font-size: 10px; padding: 5px;")
        info_label.setWordWrap(True)
        content_layout.addWidget(info_label)

        content.setLayout(content_layout)
        self.group_box.setContentWidget(content)

        layout.addWidget(self.group_box)
        self.setLayout(layout)

    def load_settings(self):
        """Load settings from config"""
        self.base_size_spin.setValue(self.config.get_base_size())
        self.image_size_spin.setValue(self.config.get_image_size())
        self.crop_mode_check.setChecked(self.config.get_crop_mode())
        self.test_compress_check.setChecked(self.config.get_test_compress())
        self.include_caption_check.setChecked(self.config.get_include_caption())

    def on_settings_changed(self):
        """Handle settings changed"""
        settings = self.get_settings()
        self.settings_changed_signal.emit(settings)

    def get_settings(self) -> dict:
        """Get current settings

        Returns:
            Dictionary of current settings
        """
        return {
            'base_size': self.base_size_spin.value(),
            'image_size': self.image_size_spin.value(),
            'crop_mode': self.crop_mode_check.isChecked(),
            'test_compress': self.test_compress_check.isChecked(),
            'include_caption': self.include_caption_check.isChecked()
        }

    def reset_to_defaults(self):
        """Reset settings to default values"""
        self.base_size_spin.setValue(1024)
        self.image_size_spin.setValue(640)
        self.crop_mode_check.setChecked(True)
        self.test_compress_check.setChecked(False)
        self.include_caption_check.setChecked(False)

        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Reset Complete",
            "Settings have been reset to default values."
        )

    def save_as_default(self):
        """Save current settings as default"""
        settings = self.get_settings()

        # Save to config
        self.config.set_base_size(settings['base_size'])
        self.config.set_image_size(settings['image_size'])
        self.config.set_crop_mode(settings['crop_mode'])
        self.config.set_test_compress(settings['test_compress'])
        self.config.set_include_caption(settings['include_caption'])
        self.config.sync()

        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Saved",
            "Current settings have been saved as default!"
        )
