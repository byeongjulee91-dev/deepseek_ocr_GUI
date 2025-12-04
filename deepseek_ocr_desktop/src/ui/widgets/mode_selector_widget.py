"""
Mode Selector Widget
Allows selection between 4 OCR modes with dynamic input fields
Adapted from frontend/src/components/ModeSelector.jsx
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QButtonGroup, QPushButton, QLineEdit, QTextEdit, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from utils.config import AppConfig


class ModeSelectorWidget(QWidget):
    """Widget for selecting OCR mode and providing mode-specific inputs"""

    mode_changed_signal = Signal(str)  # Emits mode name
    find_term_changed_signal = Signal(str)  # Emits find term
    prompt_changed_signal = Signal(str)  # Emits custom prompt

    # Mode definitions
    MODES = {
        'plain_ocr': {
            'icon': '🔤',
            'name': 'Plain OCR',
            'description': 'Extract all text from image',
            'color': '#3b82f6',  # Blue
            'requires_input': False,
        },
        'describe': {
            'icon': '👁️',
            'name': 'Describe',
            'description': 'Generate image description',
            'color': '#8b5cf6',  # Purple
            'requires_input': False,
        },
        'find_ref': {
            'icon': '🔍',
            'name': 'Find',
            'description': 'Locate specific text with bounding boxes',
            'color': '#f59e0b',  # Orange
            'requires_input': 'find_term',
        },
        'freeform': {
            'icon': '✨',
            'name': 'Freeform',
            'description': 'Custom prompt for specialized tasks',
            'color': '#ec4899',  # Pink
            'requires_input': 'prompt',
        },
    }

    def __init__(self, parent=None, config=None):
        """Initialize mode selector widget

        Args:
            parent: Parent widget
            config: AppConfig instance for settings
        """
        super().__init__(parent)
        self.config = config
        self.current_mode = 'plain_ocr'
        self.setup_ui()

    def setup_ui(self):
        """Setup widget UI"""
        layout = QVBoxLayout()

        # Get font size from config or use default
        font_size = self.config.get_ui_font_size() if self.config else 12
        title_font_size = font_size + AppConfig.TITLE_FONT_SIZE_OFFSET_LARGE

        # Title
        self.title = QLabel("📋 OCR Mode")
        self.title.setStyleSheet(f"font-size: {title_font_size}px; font-weight: bold; padding: 5px;")
        layout.addWidget(self.title)

        # Mode buttons in grid (2x2)
        button_widget = QWidget()
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)

        # Create button group for exclusive selection
        self.button_group = QButtonGroup()
        self.mode_buttons = {}

        # First row: Plain OCR, Describe
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        self.create_mode_button('plain_ocr', row1)
        self.create_mode_button('describe', row1)
        button_layout.addLayout(row1)

        # Second row: Find, Freeform
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        self.create_mode_button('find_ref', row2)
        self.create_mode_button('freeform', row2)
        button_layout.addLayout(row2)

        button_widget.setLayout(button_layout)
        layout.addWidget(button_widget)

        # Dynamic input area
        self.input_group = QGroupBox("Mode Settings")
        self.input_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        input_layout = QVBoxLayout()

        # Find term input (for find_ref mode)
        self.find_term_widget = QWidget()
        find_layout = QVBoxLayout()
        find_layout.setContentsMargins(0, 0, 0, 0)
        find_label = QLabel("Enter term to find:")
        find_label.setStyleSheet("color: #0ea5e9; font-weight: normal;")
        find_layout.addWidget(find_label)

        self.find_term_input = QLineEdit()
        self.find_term_input.setPlaceholderText("e.g., Total, Invoice #, Email")
        self.find_term_input.textChanged.connect(self.on_find_term_changed)
        find_layout.addWidget(self.find_term_input)

        self.find_term_widget.setLayout(find_layout)
        self.find_term_widget.setVisible(False)
        input_layout.addWidget(self.find_term_widget)

        # Custom prompt input (for freeform mode)
        self.prompt_widget = QWidget()
        prompt_layout = QVBoxLayout()
        prompt_layout.setContentsMargins(0, 0, 0, 0)
        prompt_label = QLabel("Enter custom prompt:")
        prompt_label.setStyleSheet("color: #0ea5e9; font-weight: normal;")
        prompt_layout.addWidget(prompt_label)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("e.g., Extract all dates and amounts from this receipt")
        self.prompt_input.setMaximumHeight(80)
        self.prompt_input.textChanged.connect(self.on_prompt_changed)
        prompt_layout.addWidget(self.prompt_input)

        self.prompt_widget.setLayout(prompt_layout)
        self.prompt_widget.setVisible(False)
        input_layout.addWidget(self.prompt_widget)

        # No input message (for plain_ocr, describe)
        self.no_input_label = QLabel("ℹ️ No additional input required for this mode")
        self.no_input_label.setStyleSheet("color: gray; padding: 10px; font-weight: normal;")
        self.no_input_label.setAlignment(Qt.AlignCenter)
        input_layout.addWidget(self.no_input_label)

        self.input_group.setLayout(input_layout)
        layout.addWidget(self.input_group)

        self.setLayout(layout)

        # Select default mode
        self.select_mode('plain_ocr')

    def create_mode_button(self, mode_id: str, parent_layout):
        """Create a mode selection button

        Args:
            mode_id: Mode identifier
            parent_layout: Parent layout to add button to
        """
        mode_info = self.MODES[mode_id]

        button = QPushButton(f"{mode_info['icon']}\n{mode_info['name']}")
        button.setCheckable(True)
        button.setMinimumHeight(70)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.05);
                border: 2px solid #444;
                border-radius: 8px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
                border-color: {mode_info['color']};
            }}
            QPushButton:checked {{
                background-color: {mode_info['color']};
                border-color: {mode_info['color']};
                color: white;
            }}
        """)
        button.setToolTip(mode_info['description'])
        button.clicked.connect(lambda: self.select_mode(mode_id))

        self.button_group.addButton(button)
        self.mode_buttons[mode_id] = button
        parent_layout.addWidget(button)

    def select_mode(self, mode_id: str):
        """Select a mode and update UI

        Args:
            mode_id: Mode identifier
        """
        if mode_id not in self.MODES:
            return

        self.current_mode = mode_id
        mode_info = self.MODES[mode_id]

        # Check the button
        self.mode_buttons[mode_id].setChecked(True)

        # Update input area visibility
        requires_input = mode_info.get('requires_input', False)

        if requires_input == 'find_term':
            self.find_term_widget.setVisible(True)
            self.prompt_widget.setVisible(False)
            self.no_input_label.setVisible(False)
            self.find_term_input.setFocus()
        elif requires_input == 'prompt':
            self.find_term_widget.setVisible(False)
            self.prompt_widget.setVisible(True)
            self.no_input_label.setVisible(False)
            self.prompt_input.setFocus()
        else:
            self.find_term_widget.setVisible(False)
            self.prompt_widget.setVisible(False)
            self.no_input_label.setVisible(True)

        # Emit signal
        self.mode_changed_signal.emit(mode_id)

    def on_find_term_changed(self):
        """Handle find term input changed"""
        text = self.find_term_input.text()
        self.find_term_changed_signal.emit(text)

    def on_prompt_changed(self):
        """Handle custom prompt input changed"""
        text = self.prompt_input.toPlainText()
        self.prompt_changed_signal.emit(text)

    def get_current_mode(self) -> str:
        """Get current mode

        Returns:
            Current mode identifier
        """
        return self.current_mode

    def get_find_term(self) -> str:
        """Get find term input

        Returns:
            Find term text
        """
        return self.find_term_input.text()

    def get_custom_prompt(self) -> str:
        """Get custom prompt input

        Returns:
            Custom prompt text
        """
        return self.prompt_input.toPlainText()

    def has_grounding(self) -> bool:
        """Check if current mode requires grounding

        Returns:
            True if mode requires grounding boxes
        """
        return self.current_mode == 'find_ref'

    def refresh_font_size(self):
        """Refresh font sizes from config"""
        if not self.config:
            return

        font_size = self.config.get_ui_font_size()
        title_font_size = font_size + AppConfig.TITLE_FONT_SIZE_OFFSET_LARGE

        # Update title
        self.title.setStyleSheet(f"font-size: {title_font_size}px; font-weight: bold; padding: 5px;")
