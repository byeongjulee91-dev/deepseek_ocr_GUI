"""
Settings Dialog
Comprehensive settings dialog for all application settings
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QLineEdit, QSpinBox, QCheckBox,
    QPushButton, QFormLayout, QGroupBox, QFileDialog,
    QMessageBox, QSlider
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
        self.reset_button.setObjectName("resetButton")
        self.reset_button.clicked.connect(self.reset_all)
        button_layout.addWidget(self.reset_button)

        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("💾 Save")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.save_settings)
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

        # vLLM group
        vllm_group = QGroupBox("vLLM Remote Inference (Optional)")
        vllm_layout = QFormLayout()

        self.use_vllm_check = QCheckBox("Use vLLM remote endpoint instead of local model")
        self.use_vllm_check.setToolTip("Connect to a remote vLLM server instead of loading model locally")
        self.use_vllm_check.toggled.connect(self.on_use_vllm_toggled)
        vllm_layout.addRow("Enable vLLM:", self.use_vllm_check)

        self.vllm_endpoint_edit = QLineEdit()
        self.vllm_endpoint_edit.setPlaceholderText("http://localhost:8000/v1")
        self.vllm_endpoint_edit.setToolTip("vLLM endpoint URL (OpenAI-compatible API)")
        vllm_layout.addRow("Endpoint URL:", self.vllm_endpoint_edit)

        self.vllm_api_key_edit = QLineEdit()
        self.vllm_api_key_edit.setPlaceholderText("(optional)")
        self.vllm_api_key_edit.setToolTip("API key for authentication (leave empty if not required)")
        self.vllm_api_key_edit.setEchoMode(QLineEdit.Password)
        vllm_layout.addRow("API Key:", self.vllm_api_key_edit)

        # Advanced vLLM settings
        self.vllm_timeout_spin = QSpinBox()
        self.vllm_timeout_spin.setMinimum(30)
        self.vllm_timeout_spin.setMaximum(3600)  # 1 hour max
        self.vllm_timeout_spin.setValue(300)
        self.vllm_timeout_spin.setSuffix(" seconds")
        self.vllm_timeout_spin.setToolTip("Request timeout for vLLM API calls (default: 300s = 5 minutes)")
        vllm_layout.addRow("Request Timeout:", self.vllm_timeout_spin)

        self.vllm_max_retries_spin = QSpinBox()
        self.vllm_max_retries_spin.setMinimum(0)
        self.vllm_max_retries_spin.setMaximum(10)
        self.vllm_max_retries_spin.setValue(3)
        self.vllm_max_retries_spin.setToolTip("Maximum retry attempts for network errors (default: 3)")
        vllm_layout.addRow("Max Retries:", self.vllm_max_retries_spin)

        # Test Connection button
        self.test_connection_button = QPushButton("🔍 Test Connection")
        self.test_connection_button.setObjectName("testButton")
        self.test_connection_button.setToolTip("Test connection to vLLM endpoint")
        self.test_connection_button.clicked.connect(self.test_vllm_connection)
        vllm_layout.addRow("", self.test_connection_button)

        vllm_group.setLayout(vllm_layout)
        layout.addWidget(vllm_group)

        # Model group (local mode)
        self.model_group = QGroupBox("Local Model Configuration")
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

        self.model_group.setLayout(model_layout)
        layout.addWidget(self.model_group)

        # Info
        info = QLabel(
            "⚠️ Changing model settings requires restarting the application.\n"
            "Model will be downloaded on next startup if not cached (local mode only)."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #f59e0b; padding: 10px; background-color: rgba(245, 158, 11, 0.1); border-radius: 6px;")
        layout.addWidget(info)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def on_use_vllm_toggled(self, checked: bool):
        """Handle vLLM checkbox toggle"""
        # Enable/disable vLLM fields
        self.vllm_endpoint_edit.setEnabled(checked)
        self.vllm_api_key_edit.setEnabled(checked)
        self.vllm_timeout_spin.setEnabled(checked)
        self.vllm_max_retries_spin.setEnabled(checked)
        self.test_connection_button.setEnabled(checked)

        # Enable/disable local model fields
        self.model_name_edit.setEnabled(not checked)
        self.hf_home_edit.setEnabled(not checked)
        self.model_group.setEnabled(not checked)

    def test_vllm_connection(self):
        """Test connection to vLLM endpoint"""
        from PySide6.QtWidgets import QProgressDialog
        from PySide6.QtCore import QTimer

        # Get current values
        endpoint = self.vllm_endpoint_edit.text().strip()
        api_key = self.vllm_api_key_edit.text().strip()
        model_name = self.model_name_edit.text().strip() or "deepseek-ai/DeepSeek-OCR"
        timeout = float(self.vllm_timeout_spin.value())
        max_retries = self.vllm_max_retries_spin.value()

        # Validate endpoint
        if not endpoint:
            QMessageBox.warning(
                self,
                "Missing Endpoint",
                "Please enter a vLLM endpoint URL.\n\n"
                "Example: http://localhost:8000/v1"
            )
            return

        # Show progress dialog
        progress = QProgressDialog("Testing connection to vLLM endpoint...", None, 0, 0, self)
        progress.setWindowTitle("Testing Connection")
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.setMinimumDuration(0)
        progress.setValue(0)

        # Import VLLMClient
        try:
            from ...core.vllm_client import VLLMClient
        except ImportError as e:
            progress.close()
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to import VLLMClient:\n{str(e)}\n\n"
                "Make sure 'openai' package is installed:\n"
                "pip install openai"
            )
            return

        # Test connection in a timer to avoid blocking UI
        def do_test():
            try:
                # Create client
                client = VLLMClient(
                    endpoint=endpoint,
                    api_key=api_key if api_key else None,
                    model_name=model_name,
                    timeout=timeout,
                    max_retries=max_retries
                )

                # Test connection
                success, message = client.test_connection()

                # Close progress dialog
                progress.close()

                # Show result
                if success:
                    QMessageBox.information(
                        self,
                        "Connection Successful",
                        f"Successfully connected to vLLM endpoint!\n\n{message}"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Connection Failed",
                        f"Failed to connect to vLLM endpoint:\n\n{message}\n\n"
                        "Please check:\n"
                        "• Endpoint URL is correct (must end with /v1)\n"
                        "• vLLM server is running\n"
                        "• Network connection is available\n"
                        "• Firewall allows the connection"
                    )

            except Exception as e:
                progress.close()
                QMessageBox.critical(
                    self,
                    "Test Failed",
                    f"Error testing connection:\n\n{type(e).__name__}: {str(e)}"
                )

        # Run test after a short delay to show progress dialog
        QTimer.singleShot(100, do_test)

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

        # Font Size group
        font_group = QGroupBox("Font Size Settings")
        font_layout = QFormLayout()

        # Result viewer font size
        result_font_layout = QHBoxLayout()
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(8)
        self.font_size_spin.setMaximum(24)
        self.font_size_spin.setSingleStep(1)
        self.font_size_spin.setSuffix(" pt")
        self.font_size_spin.setToolTip("Font size for OCR result text (8-24pt)")
        self.font_size_spin.valueChanged.connect(self.on_font_size_changed)
        result_font_layout.addWidget(self.font_size_spin)

        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setMinimum(8)
        self.font_size_slider.setMaximum(24)
        self.font_size_slider.setTickPosition(QSlider.TicksBelow)
        self.font_size_slider.setTickInterval(2)
        self.font_size_slider.valueChanged.connect(self.font_size_spin.setValue)
        self.font_size_spin.valueChanged.connect(self.font_size_slider.setValue)
        result_font_layout.addWidget(self.font_size_slider)

        font_layout.addRow("Result Text:", result_font_layout)

        # Log viewer font size
        log_font_layout = QHBoxLayout()
        self.log_font_size_spin = QSpinBox()
        self.log_font_size_spin.setMinimum(8)
        self.log_font_size_spin.setMaximum(24)
        self.log_font_size_spin.setSingleStep(1)
        self.log_font_size_spin.setSuffix(" pt")
        self.log_font_size_spin.setToolTip("Font size for log viewer (8-24pt)")
        self.log_font_size_spin.valueChanged.connect(self.on_log_font_size_changed)
        log_font_layout.addWidget(self.log_font_size_spin)

        self.log_font_size_slider = QSlider(Qt.Horizontal)
        self.log_font_size_slider.setMinimum(8)
        self.log_font_size_slider.setMaximum(24)
        self.log_font_size_slider.setTickPosition(QSlider.TicksBelow)
        self.log_font_size_slider.setTickInterval(2)
        self.log_font_size_slider.valueChanged.connect(self.log_font_size_spin.setValue)
        self.log_font_size_spin.valueChanged.connect(self.log_font_size_slider.setValue)
        log_font_layout.addWidget(self.log_font_size_slider)

        font_layout.addRow("Log Viewer:", log_font_layout)

        # UI font size (Control Panel, buttons, labels)
        ui_font_layout = QHBoxLayout()
        self.ui_font_size_spin = QSpinBox()
        self.ui_font_size_spin.setMinimum(8)
        self.ui_font_size_spin.setMaximum(24)
        self.ui_font_size_spin.setSingleStep(1)
        self.ui_font_size_spin.setSuffix(" pt")
        self.ui_font_size_spin.setToolTip("Font size for Control Panel and UI elements (8-24pt)")
        ui_font_layout.addWidget(self.ui_font_size_spin)

        self.ui_font_size_slider = QSlider(Qt.Horizontal)
        self.ui_font_size_slider.setMinimum(8)
        self.ui_font_size_slider.setMaximum(24)
        self.ui_font_size_slider.setTickPosition(QSlider.TicksBelow)
        self.ui_font_size_slider.setTickInterval(2)
        self.ui_font_size_slider.valueChanged.connect(self.ui_font_size_spin.setValue)
        self.ui_font_size_spin.valueChanged.connect(self.ui_font_size_slider.setValue)
        ui_font_layout.addWidget(self.ui_font_size_slider)

        font_layout.addRow("Control Panel:", ui_font_layout)

        # Preview label
        self.font_preview_label = QLabel("AaBbCc 가나다라 123 - Preview text")
        self.font_preview_label.setStyleSheet("""
            padding: 10px;
            background-color: #2d2d2d;
            border-radius: 4px;
            color: #d4d4d4;
        """)
        font_layout.addRow("Preview:", self.font_preview_label)

        font_group.setLayout(font_layout)
        layout.addWidget(font_group)

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

        # Startup group
        startup_group = QGroupBox("Startup Settings")
        startup_layout = QVBoxLayout()

        self.skip_startup_dialog_check = QCheckBox("Skip model selection dialog on startup")
        self.skip_startup_dialog_check.setToolTip(
            "Automatically start with saved model mode (Local/vLLM)\n"
            "Uncheck to show mode selection dialog on next startup"
        )
        startup_layout.addWidget(self.skip_startup_dialog_check)

        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)

        # Clear cache button
        clear_cache_button = QPushButton("🗑️ Clear Window State")
        clear_cache_button.setObjectName("clearButton")
        clear_cache_button.setToolTip("Clear saved window geometry and state")
        clear_cache_button.clicked.connect(self.clear_window_state)
        layout.addWidget(clear_cache_button)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def on_font_size_changed(self, size: int):
        """Update preview label with new font size"""
        font = QFont("Courier New", size)
        self.font_preview_label.setFont(font)

    def on_log_font_size_changed(self, size: int):
        """Handle log font size change (for preview only)"""
        pass  # Preview only uses result font size

    def load_settings(self):
        """Load current settings from config"""
        # vLLM settings
        use_vllm = self.config.get_use_vllm()
        self.use_vllm_check.setChecked(use_vllm)
        self.vllm_endpoint_edit.setText(self.config.get_vllm_endpoint())
        self.vllm_api_key_edit.setText(self.config.get_vllm_api_key())
        self.vllm_timeout_spin.setValue(int(self.config.get_vllm_timeout()))
        self.vllm_max_retries_spin.setValue(self.config.get_vllm_max_retries())

        # Trigger toggle to enable/disable fields
        self.on_use_vllm_toggled(use_vllm)

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

        # UI settings - Font sizes
        font_size = self.config.get_font_size()
        self.font_size_spin.setValue(font_size)
        self.font_size_slider.setValue(font_size)
        self.on_font_size_changed(font_size)  # Update preview

        log_font_size = self.config.get_log_font_size()
        self.log_font_size_spin.setValue(log_font_size)
        self.log_font_size_slider.setValue(log_font_size)

        ui_font_size = self.config.get_ui_font_size()
        self.ui_font_size_spin.setValue(ui_font_size)
        self.ui_font_size_slider.setValue(ui_font_size)

        # UI settings - Window
        self.restore_geometry_check.setChecked(True)  # Always enabled for now
        self.restore_splitter_check.setChecked(True)

        # UI settings - Startup
        self.skip_startup_dialog_check.setChecked(self.config.get_skip_startup_dialog())

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
        # vLLM settings
        self.config.set_use_vllm(self.use_vllm_check.isChecked())
        self.config.set_vllm_endpoint(self.vllm_endpoint_edit.text())
        self.config.set_vllm_api_key(self.vllm_api_key_edit.text())
        self.config.set_vllm_timeout(float(self.vllm_timeout_spin.value()))
        self.config.set_vllm_max_retries(self.vllm_max_retries_spin.value())

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

        # UI settings - Font sizes
        self.config.set_font_size(self.font_size_spin.value())
        self.config.set_log_font_size(self.log_font_size_spin.value())
        self.config.set_ui_font_size(self.ui_font_size_spin.value())

        # UI settings - Startup
        self.config.set_skip_startup_dialog(self.skip_startup_dialog_check.isChecked())

        # Sync to disk
        self.config.sync()

        # Show success message
        msg = "Settings have been saved successfully!\n\n"
        msg += "Font size changes will be applied immediately.\n\n"
        if self.use_vllm_check.isChecked():
            msg += "⚠️ vLLM mode enabled - restart the application to connect to remote endpoint."
        else:
            msg += "⚠️ Model changes require restarting the application."

        QMessageBox.information(
            self,
            "Settings Saved",
            msg
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
            # vLLM settings
            self.use_vllm_check.setChecked(False)
            self.vllm_endpoint_edit.setText("http://localhost:8000/v1")
            self.vllm_api_key_edit.setText("")
            self.vllm_timeout_spin.setValue(300)
            self.vllm_max_retries_spin.setValue(3)
            self.on_use_vllm_toggled(False)

            # Model settings
            self.model_name_edit.setText("deepseek-ai/DeepSeek-OCR")
            self.hf_home_edit.setText("~/.cache/huggingface")

            # Processing settings
            self.base_size_spin.setValue(1024)
            self.image_size_spin.setValue(640)
            self.crop_mode_check.setChecked(True)
            self.test_compress_check.setChecked(False)
            self.include_caption_check.setChecked(False)

            # PDF settings
            self.pdf_dpi_spin.setValue(144)
            self.extract_images_check.setChecked(True)

            # Reset font sizes to defaults
            self.font_size_spin.setValue(12)
            self.font_size_slider.setValue(12)
            self.log_font_size_spin.setValue(11)
            self.log_font_size_slider.setValue(11)
            self.ui_font_size_spin.setValue(12)
            self.ui_font_size_slider.setValue(12)
            self.on_font_size_changed(12)  # Update preview

            QMessageBox.information(
                self,
                "Reset Complete",
                "All settings have been reset to defaults.\n\n"
                "Click 'Save' to apply the changes."
            )
