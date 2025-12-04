"""
PDF Processor Widget
Handles PDF upload, format selection, and processing progress
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QProgressBar, QPushButton, QGroupBox,
    QSpinBox, QCheckBox, QFormLayout, QTextEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ...utils.config import AppConfig


class PDFProcessorWidget(QWidget):
    """Widget for PDF processing configuration and progress"""

    # Signals
    format_changed_signal = Signal(str)  # Emits selected format
    dpi_changed_signal = Signal(int)  # Emits DPI value
    extract_images_changed_signal = Signal(bool)  # Emits extract images flag

    def __init__(self, parent=None, config=None):
        """Initialize PDF processor widget

        Args:
            parent: Parent widget
            config: AppConfig instance for settings
        """
        super().__init__(parent)
        self.config = config
        self.setup_ui()

    def setup_ui(self):
        """Setup widget UI"""
        layout = QVBoxLayout()

        # Get font size from config or use default
        font_size = self.config.get_ui_font_size() if self.config else 12
        title_font_size = font_size + AppConfig.TITLE_FONT_SIZE_OFFSET_LARGE

        # Title
        self.title = QLabel("📄 PDF Processing")
        self.title.setStyleSheet(f"font-size: {title_font_size}px; font-weight: bold; padding: 5px;")
        layout.addWidget(self.title)

        # Output format selector
        format_group = QGroupBox("Output Format")
        format_layout = QVBoxLayout()

        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "Markdown (.md)",
            "HTML (.html)",
            "Word Document (.docx)",
            "JSON (.json)"
        ])
        self.format_combo.currentIndexChanged.connect(self.on_format_changed)

        format_help = QLabel("💡 Select output format for processed PDF")
        format_help.setStyleSheet("color: gray; font-size: 10px; padding: 5px;")
        format_help.setWordWrap(True)

        format_layout.addWidget(self.format_combo)
        format_layout.addWidget(format_help)
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        # PDF Settings
        settings_group = QGroupBox("PDF Settings")
        settings_layout = QFormLayout()

        # DPI setting
        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setMinimum(72)
        self.dpi_spinbox.setMaximum(300)
        self.dpi_spinbox.setValue(144)
        self.dpi_spinbox.setSingleStep(12)
        self.dpi_spinbox.setSuffix(" DPI")
        self.dpi_spinbox.setToolTip("Higher DPI = better quality but slower processing")
        self.dpi_spinbox.valueChanged.connect(self.on_dpi_changed)
        settings_layout.addRow("Resolution:", self.dpi_spinbox)

        # Extract images option
        self.extract_images_checkbox = QCheckBox("Extract embedded images")
        self.extract_images_checkbox.setChecked(True)
        self.extract_images_checkbox.setToolTip("Extract and save images found in the PDF")
        self.extract_images_checkbox.stateChanged.connect(self.on_extract_images_changed)
        settings_layout.addRow("", self.extract_images_checkbox)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Progress area
        progress_group = QGroupBox("Processing Progress")
        progress_layout = QVBoxLayout()

        # Status label
        self.status_label = QLabel("Ready to process PDF")
        self.status_label.setStyleSheet("color: #0ea5e9; font-weight: bold;")
        progress_layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("0 / 0 pages")
        progress_layout.addWidget(self.progress_bar)

        # Page details
        self.page_details = QTextEdit()
        self.page_details.setReadOnly(True)
        self.page_details.setMaximumHeight(100)
        self.page_details.setPlaceholderText("Page processing details will appear here...")
        font = QFont("Courier New", 9)
        self.page_details.setFont(font)
        progress_layout.addWidget(self.page_details)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # Result actions (hidden initially)
        self.result_group = QGroupBox("Result")
        result_layout = QVBoxLayout()

        self.result_label = QLabel("Processing complete!")
        self.result_label.setStyleSheet("color: #10b981; font-weight: bold;")
        result_layout.addWidget(self.result_label)

        # Download button
        self.download_button = QPushButton("💾 Save Document")
        self.download_button.clicked.connect(self.on_download_clicked)
        self.download_button.setMinimumHeight(40)
        self.download_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        result_layout.addWidget(self.download_button)

        self.result_group.setLayout(result_layout)
        self.result_group.setVisible(False)
        layout.addWidget(self.result_group)

        layout.addStretch()
        self.setLayout(layout)

        # Store result data
        self.current_result = None

    def on_format_changed(self, index):
        """Handle format selection changed"""
        formats = ['markdown', 'html', 'docx', 'json']
        if 0 <= index < len(formats):
            self.format_changed_signal.emit(formats[index])

    def on_dpi_changed(self, value):
        """Handle DPI value changed"""
        self.dpi_changed_signal.emit(value)

    def on_extract_images_changed(self, state):
        """Handle extract images checkbox changed"""
        self.extract_images_changed_signal.emit(state == Qt.Checked)

    def get_selected_format(self) -> str:
        """Get selected output format

        Returns:
            Format identifier ('markdown', 'html', 'docx', 'json')
        """
        formats = ['markdown', 'html', 'docx', 'json']
        index = self.format_combo.currentIndex()
        return formats[index] if 0 <= index < len(formats) else 'markdown'

    def get_dpi(self) -> int:
        """Get selected DPI value

        Returns:
            DPI value
        """
        return self.dpi_spinbox.value()

    def get_extract_images(self) -> bool:
        """Get extract images setting

        Returns:
            True if images should be extracted
        """
        return self.extract_images_checkbox.isChecked()

    def reset_progress(self):
        """Reset progress display"""
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0 / 0 pages")
        self.status_label.setText("Ready to process PDF")
        self.status_label.setStyleSheet("color: #0ea5e9; font-weight: bold;")
        self.page_details.clear()
        self.result_group.setVisible(False)
        self.current_result = None

    def update_progress(self, current_page: int, total_pages: int):
        """Update progress bar

        Args:
            current_page: Current page number (1-indexed)
            total_pages: Total number of pages
        """
        if total_pages > 0:
            percentage = int((current_page / total_pages) * 100)
            self.progress_bar.setValue(percentage)
            self.progress_bar.setFormat(f"{current_page} / {total_pages} pages")

    def update_status(self, message: str):
        """Update status message

        Args:
            message: Status message
        """
        self.status_label.setText(message)

    def add_page_detail(self, page_num: int, detail: str):
        """Add page processing detail

        Args:
            page_num: Page number
            detail: Detail message
        """
        self.page_details.append(f"[Page {page_num}] {detail}")

    def show_complete(self, result: dict):
        """Show processing complete state

        Args:
            result: Processing result dictionary
        """
        self.current_result = result
        total_pages = result.get('total_pages', 0)
        format_name = result.get('format', 'document')

        self.status_label.setText(f"✅ Complete! {total_pages} pages processed.")
        self.status_label.setStyleSheet("color: #10b981; font-weight: bold;")
        self.progress_bar.setValue(100)

        # Update result label
        self.result_label.setText(
            f"✅ {total_pages} pages processed successfully!\n"
            f"Format: {format_name.upper()}"
        )

        # Show result group
        self.result_group.setVisible(True)

    def show_error(self, error_message: str):
        """Show error state

        Args:
            error_message: Error message
        """
        self.status_label.setText(f"❌ Error: {error_message}")
        self.status_label.setStyleSheet("color: #ef4444; font-weight: bold;")
        self.page_details.append(f"\n❌ ERROR: {error_message}")

    def on_download_clicked(self):
        """Handle download button clicked"""
        if not self.current_result:
            return

        # Get format and content
        format_name = self.current_result.get('format', 'markdown')
        content = self.current_result.get('content')

        if not content:
            QMessageBox.warning(self, "No Content", "No content available to save.")
            return

        # File extensions
        extensions = {
            'markdown': '.md',
            'html': '.html',
            'docx': '.docx',
            'json': '.json'
        }

        # File filters
        filters = {
            'markdown': "Markdown Files (*.md);;All Files (*)",
            'html': "HTML Files (*.html);;All Files (*)",
            'docx': "Word Documents (*.docx);;All Files (*)",
            'json': "JSON Files (*.json);;All Files (*)"
        }

        ext = extensions.get(format_name, '.txt')
        filter_str = filters.get(format_name, "All Files (*)")

        # Show save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Processed PDF",
            f"processed_pdf{ext}",
            filter_str
        )

        if file_path:
            try:
                # Save content
                if format_name == 'docx':
                    # DOCX is binary
                    with open(file_path, 'wb') as f:
                        f.write(content)
                else:
                    # Text formats
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                QMessageBox.information(
                    self,
                    "Saved",
                    f"Document saved successfully!\n\n{file_path}"
                )

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Save Error",
                    f"Failed to save document:\n\n{str(e)}"
                )

    def refresh_font_size(self):
        """Refresh font sizes from config"""
        if not self.config:
            return

        font_size = self.config.get_ui_font_size()
        title_font_size = font_size + AppConfig.TITLE_FONT_SIZE_OFFSET_LARGE

        # Update title
        self.title.setStyleSheet(f"font-size: {title_font_size}px; font-weight: bold; padding: 5px;")
