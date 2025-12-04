"""
Result Viewer Widget
Displays OCR results with text rendering
Adapted from frontend/src/components/ResultPanel.jsx
"""

import re
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTextEdit, QLabel, QPushButton, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextOption

# Import bounding box canvas
from .bounding_box_canvas import ImageWithBoxesWidget
from ...utils.config import AppConfig


class ResultViewerWidget(QWidget):
    """Widget for displaying OCR results"""

    def __init__(self, config=None, parent=None):
        """Initialize result viewer widget

        Args:
            config: AppConfig instance for settings
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config
        self.current_result = None
        self.current_image_path = None
        self._font_size = 12  # Default font size
        self.setup_ui()

    def setup_ui(self):
        """Setup widget UI"""
        layout = QVBoxLayout()

        # Tab widget for different views
        self.tab_widget = QTabWidget()

        # Text tab
        self.text_tab = self.create_text_tab()
        self.tab_widget.addTab(self.text_tab, "📝 Text")

        # Image tab (with bounding boxes)
        self.image_tab = self.create_image_tab()
        self.tab_widget.addTab(self.image_tab, "🖼️ Image")

        # Debug tab
        self.debug_tab = self.create_debug_tab()
        self.tab_widget.addTab(self.debug_tab, "🐛 Debug")

        layout.addWidget(self.tab_widget)

        # Action buttons
        button_layout = QHBoxLayout()

        self.copy_button = QPushButton("📋 Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.copy_button.setEnabled(False)
        button_layout.addWidget(self.copy_button)

        self.download_button = QPushButton("💾 Download as Text")
        self.download_button.clicked.connect(self.download_result)
        self.download_button.setEnabled(False)
        button_layout.addWidget(self.download_button)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def create_text_tab(self) -> QWidget:
        """Create text display tab

        Returns:
            Text tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout()

        # Result text edit
        self.result_text_edit = QTextEdit()
        self.result_text_edit.setReadOnly(True)
        self.result_text_edit.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)

        # Set monospace font for plain text (get size from config)
        self._font_size = self.config.get_font_size() if self.config else 12
        font = QFont("Courier New", self._font_size)
        self.result_text_edit.setFont(font)

        layout.addWidget(self.result_text_edit)

        tab.setLayout(layout)
        return tab

    def create_image_tab(self) -> QWidget:
        """Create image display tab with bounding boxes

        Returns:
            Image tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout()

        # Image with boxes widget
        self.image_with_boxes = ImageWithBoxesWidget()
        layout.addWidget(self.image_with_boxes)

        # Info label
        self.image_info_label = QLabel("No image to display")
        self.image_info_label.setAlignment(Qt.AlignCenter)
        self.image_info_label.setStyleSheet("color: gray; padding: 20px;")
        layout.addWidget(self.image_info_label)

        tab.setLayout(layout)
        return tab

    def create_debug_tab(self) -> QWidget:
        """Create debug info tab

        Returns:
            Debug tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout()

        # Raw model response
        raw_label = QLabel("Raw Model Response:")
        raw_label.setStyleSheet("font-weight: bold; color: #0ea5e9;")
        layout.addWidget(raw_label)

        self.raw_text_edit = QTextEdit()
        self.raw_text_edit.setReadOnly(True)
        # Debug tab uses slightly smaller font
        debug_font_size = max(self._font_size - 2, 8)
        font = QFont("Courier New", debug_font_size)
        self.raw_text_edit.setFont(font)
        layout.addWidget(self.raw_text_edit)

        # Metadata
        metadata_label = QLabel("Metadata:")
        metadata_label.setStyleSheet("font-weight: bold; color: #0ea5e9; margin-top: 10px;")
        layout.addWidget(metadata_label)

        self.metadata_text_edit = QTextEdit()
        self.metadata_text_edit.setReadOnly(True)
        self.metadata_text_edit.setMaximumHeight(150)
        self.metadata_text_edit.setFont(font)
        layout.addWidget(self.metadata_text_edit)

        tab.setLayout(layout)
        return tab

    def update_font_size(self, size: int = None):
        """Update font size for all text editors

        Args:
            size: Font size in points. If None, reads from config.
        """
        if size is None and self.config:
            size = self.config.get_font_size()
        elif size is None:
            size = 12  # Default

        self._font_size = size

        # Update main result text edit
        font = QFont("Courier New", size)
        self.result_text_edit.setFont(font)

        # Update debug text edits (slightly smaller)
        debug_font_size = max(size + AppConfig.DEBUG_FONT_SIZE_OFFSET, 8)
        debug_font = QFont("Courier New", debug_font_size)
        self.raw_text_edit.setFont(debug_font)
        self.metadata_text_edit.setFont(debug_font)

    def refresh_settings(self):
        """Refresh settings from config (call after settings dialog closes)"""
        if self.config:
            self.update_font_size(self.config.get_font_size())

    def display_result(self, result: dict, image_path: str = None):
        """Display OCR result

        Args:
            result: OCR result dict with keys: text, raw_text, boxes, image_dims, metadata
            image_path: Path to source image (for bounding box display)
        """
        self.current_result = result
        self.current_image_path = image_path

        # Display text
        text = result.get('text', '')
        self.display_text(text)

        # Display image with bounding boxes
        boxes = result.get('boxes', [])
        image_dims = result.get('image_dims', {})

        if image_path and boxes:
            self.image_with_boxes.display_image_with_boxes(image_path, boxes, image_dims)
            self.image_info_label.setText(f"📦 {len(boxes)} bounding box(es) detected")
            self.image_info_label.setStyleSheet("color: #0ea5e9; padding: 10px; font-weight: bold;")
        elif image_path:
            self.image_with_boxes.display_image_with_boxes(image_path, [], image_dims)
            self.image_info_label.setText("✅ Image processed - no bounding boxes")
            self.image_info_label.setStyleSheet("color: gray; padding: 10px;")
        else:
            self.image_with_boxes.clear()
            self.image_info_label.setText("No image to display")
            self.image_info_label.setStyleSheet("color: gray; padding: 10px;")

        # Display raw response
        raw_text = result.get('raw_text', '')
        self.raw_text_edit.setPlainText(raw_text)
        self.raw_text_edit.append(f"\n\n📊 Character count: {len(raw_text)}")

        # Display metadata
        metadata = result.get('metadata', {})
        boxes = result.get('boxes', [])
        image_dims = result.get('image_dims', {})

        metadata_str = json.dumps(metadata, indent=2)
        metadata_str += f"\n\n📦 Bounding boxes: {len(boxes)}"
        if boxes:
            metadata_str += "\nBox coordinates:"
            for idx, box_data in enumerate(boxes):
                label = box_data.get('label', 'unknown')
                box = box_data.get('box', [])
                metadata_str += f"\n  {idx+1}. {label}: {box}"

        if image_dims:
            metadata_str += f"\n\n📐 Image dimensions: {image_dims.get('w')}x{image_dims.get('h')}"

        self.metadata_text_edit.setPlainText(metadata_str)

        # Enable buttons
        self.copy_button.setEnabled(True)
        self.download_button.setEnabled(True)

    def display_text(self, text: str):
        """Display text with auto-detection of format

        Args:
            text: Text to display
        """
        # Detect format
        if self.is_html(text):
            # HTML mode
            self.result_text_edit.setHtml(text)
        elif self.is_markdown(text):
            # Markdown mode - convert to HTML
            try:
                import markdown
                html = markdown.markdown(text, extensions=['tables', 'fenced_code'])
                self.result_text_edit.setHtml(html)
            except ImportError:
                # Fallback to plain text if markdown module not available
                self.result_text_edit.setPlainText(text)
        else:
            # Plain text mode
            self.result_text_edit.setPlainText(text)

    def is_html(self, text: str) -> bool:
        """Check if text appears to be HTML

        Args:
            text: Text to check

        Returns:
            True if text appears to be HTML
        """
        html_tags = ['<table>', '<tr>', '<td>', '<div>', '<p>', '<h1>', '<h2>']
        return any(tag in text for tag in html_tags)

    def is_markdown(self, text: str) -> bool:
        """Check if text appears to be Markdown

        Args:
            text: Text to check

        Returns:
            True if text appears to be Markdown
        """
        markdown_patterns = [
            r'^#+\s',        # Headers
            r'\*\*.*\*\*',   # Bold
            r'```',          # Code blocks
            r'^\*\s',        # Lists
            r'^\d+\.\s',     # Numbered lists
            r'\|.*\|',       # Tables
        ]

        for pattern in markdown_patterns:
            if re.search(pattern, text, re.MULTILINE):
                return True
        return False

    def copy_to_clipboard(self):
        """Copy result text to clipboard"""
        from PySide6.QtWidgets import QApplication

        if self.current_result:
            text = self.current_result.get('text', '')
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

            QMessageBox.information(
                self,
                "Copied",
                "Result copied to clipboard!"
            )

    def download_result(self):
        """Download result as text file"""
        if not self.current_result:
            return

        text = self.current_result.get('text', '')

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save OCR Result",
            "ocr_result.txt",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)

                QMessageBox.information(
                    self,
                    "Saved",
                    f"Result saved to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save file:\n{str(e)}"
                )

    def clear(self):
        """Clear all displays"""
        self.current_result = None
        self.current_image_path = None
        self.result_text_edit.clear()
        self.raw_text_edit.clear()
        self.metadata_text_edit.clear()
        self.image_with_boxes.clear()
        self.image_info_label.setText("No image to display")
        self.image_info_label.setStyleSheet("color: gray; padding: 10px;")
        self.copy_button.setEnabled(False)
        self.download_button.setEnabled(False)

    def show_loading(self):
        """Show loading state"""
        self.result_text_edit.setPlainText("⏳ Processing your image...\n\nThis may take 10-30 seconds.")
        self.tab_widget.setCurrentIndex(0)  # Switch to text tab

    def show_error(self, error_message: str):
        """Show error message

        Args:
            error_message: Error message to display
        """
        self.result_text_edit.setPlainText(f"❌ Error:\n\n{error_message}")
        self.copy_button.setEnabled(False)
        self.download_button.setEnabled(False)
