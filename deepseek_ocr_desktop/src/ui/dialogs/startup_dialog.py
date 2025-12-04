"""
Startup Mode Selection Dialog
Allows user to choose between Local Model and vLLM before model loading
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton,
    QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton,
    QGroupBox, QFormLayout, QButtonGroup, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class StartupDialog(QDialog):
    """Dialog for selecting model mode at startup"""

    def __init__(self, config, parent=None):
        """Initialize startup dialog

        Args:
            config: AppConfig instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        self.selected_mode = None  # Will be 'local' or 'vllm'
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("DeepSeek-OCR - Model Selection")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QVBoxLayout()

        # Title
        title_label = QLabel("🚀 Select OCR Model Mode")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(
            "Choose how to run the DeepSeek-OCR model:\n"
            "• Local Model: Run on your GPU (requires 8-12GB VRAM)\n"
            "• vLLM Server: Connect to remote vLLM endpoint"
        )
        desc_label.setStyleSheet("color: gray; padding: 10px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Mode selection
        mode_group = QGroupBox("Model Mode")
        mode_layout = QVBoxLayout()

        self.mode_button_group = QButtonGroup(self)

        # Local mode radio button
        self.local_radio = QRadioButton("🖥️  Local Model (Transformer)")
        self.local_radio.setToolTip("Load model locally on your GPU")
        self.local_radio.toggled.connect(self.on_mode_changed)
        self.mode_button_group.addButton(self.local_radio)
        mode_layout.addWidget(self.local_radio)

        # vLLM mode radio button
        self.vllm_radio = QRadioButton("🌐 Remote vLLM Server")
        self.vllm_radio.setToolTip("Connect to remote vLLM endpoint")
        self.vllm_radio.toggled.connect(self.on_mode_changed)
        self.mode_button_group.addButton(self.vllm_radio)
        mode_layout.addWidget(self.vllm_radio)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # vLLM settings (initially hidden)
        self.vllm_settings_group = QGroupBox("vLLM Server Settings")
        vllm_layout = QFormLayout()

        # Endpoint
        self.endpoint_input = QLineEdit()
        self.endpoint_input.setPlaceholderText("http://localhost:8000/v1")
        self.endpoint_input.setToolTip("vLLM server endpoint URL")
        vllm_layout.addRow("Endpoint URL:", self.endpoint_input)

        # API Key (optional)
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Optional API key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setToolTip("API key for authentication (leave blank if not required)")

        # Show/hide password button
        api_key_layout = QHBoxLayout()
        api_key_layout.setContentsMargins(0, 0, 0, 0)
        api_key_layout.setSpacing(5)
        api_key_layout.addWidget(self.api_key_input, 1)  # Stretch factor 1
        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setFixedWidth(35)
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.toggled.connect(self.toggle_password_visibility)
        self.show_password_btn.setToolTip("Show/hide API key")
        api_key_layout.addWidget(self.show_password_btn, 0)  # Stretch factor 0

        api_key_widget = QWidget()
        api_key_widget.setLayout(api_key_layout)
        vllm_layout.addRow("API Key:", api_key_widget)

        # Timeout
        self.timeout_input = QDoubleSpinBox()
        self.timeout_input.setMinimum(10.0)
        self.timeout_input.setMaximum(3600.0)
        self.timeout_input.setValue(300.0)
        self.timeout_input.setSingleStep(10.0)
        self.timeout_input.setSuffix(" seconds")
        self.timeout_input.setToolTip("Request timeout duration")
        vllm_layout.addRow("Timeout:", self.timeout_input)

        # Max Retries
        self.max_retries_input = QSpinBox()
        self.max_retries_input.setMinimum(0)
        self.max_retries_input.setMaximum(10)
        self.max_retries_input.setValue(3)
        self.max_retries_input.setToolTip("Maximum retry attempts for failed requests")
        vllm_layout.addRow("Max Retries:", self.max_retries_input)

        self.vllm_settings_group.setLayout(vllm_layout)
        self.vllm_settings_group.setVisible(False)
        layout.addWidget(self.vllm_settings_group)

        # Auto-start checkbox
        self.auto_start_checkbox = QCheckBox("Remember this choice and skip this dialog next time")
        self.auto_start_checkbox.setToolTip("Save settings and automatically start with selected mode")
        layout.addWidget(self.auto_start_checkbox)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.start_button = QPushButton("Start")
        self.start_button.setDefault(True)
        self.start_button.clicked.connect(self.on_start_clicked)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        button_layout.addWidget(self.start_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def toggle_password_visibility(self, checked):
        """Toggle API key visibility"""
        if checked:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)

    def load_settings(self):
        """Load settings from config"""
        # Load mode
        use_vllm = self.config.get_use_vllm()
        if use_vllm:
            self.vllm_radio.setChecked(True)
        else:
            self.local_radio.setChecked(True)

        # Load vLLM settings
        self.endpoint_input.setText(self.config.get_vllm_endpoint())
        self.api_key_input.setText(self.config.get_vllm_api_key())
        self.timeout_input.setValue(self.config.get_vllm_timeout())
        self.max_retries_input.setValue(self.config.get_vllm_max_retries())

    def on_mode_changed(self):
        """Handle mode selection changed"""
        is_vllm = self.vllm_radio.isChecked()
        self.vllm_settings_group.setVisible(is_vllm)

        # Update button text
        if is_vllm:
            self.start_button.setText("Connect to vLLM")
        else:
            self.start_button.setText("Load Local Model")

    def on_start_clicked(self):
        """Handle start button clicked"""
        # Save settings if auto-start is enabled
        if self.auto_start_checkbox.isChecked():
            self.save_settings()
            self.config.set_skip_startup_dialog(True)
        else:
            # Save vLLM settings even if not auto-starting
            # so they are remembered for next time
            if self.vllm_radio.isChecked():
                self.save_vllm_settings()

        # Set selected mode
        self.selected_mode = 'vllm' if self.vllm_radio.isChecked() else 'local'

        self.accept()

    def save_settings(self):
        """Save all settings to config"""
        # Save mode
        use_vllm = self.vllm_radio.isChecked()
        self.config.set_use_vllm(use_vllm)

        # Save vLLM settings
        if use_vllm:
            self.save_vllm_settings()

        self.config.sync()

    def save_vllm_settings(self):
        """Save vLLM settings to config"""
        self.config.set_vllm_endpoint(self.endpoint_input.text())
        self.config.set_vllm_api_key(self.api_key_input.text())
        self.config.set_vllm_timeout(self.timeout_input.value())
        self.config.set_vllm_max_retries(self.max_retries_input.value())

    def get_mode(self) -> str:
        """Get selected mode

        Returns:
            'local' or 'vllm'
        """
        return self.selected_mode

    def get_vllm_settings(self) -> dict:
        """Get vLLM settings

        Returns:
            Dictionary with vLLM configuration
        """
        return {
            'endpoint': self.endpoint_input.text(),
            'api_key': self.api_key_input.text(),
            'timeout': self.timeout_input.value(),
            'max_retries': self.max_retries_input.value()
        }
