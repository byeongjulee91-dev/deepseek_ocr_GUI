"""
Image Upload Widget
Supports drag-and-drop, file browser, and clipboard paste
Adapted from frontend/src/components/ImageUpload.jsx
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QImage


class ImageUploadWidget(QWidget):
    """Widget for uploading images via drag-drop, file browser, or clipboard"""

    file_selected_signal = Signal(str)  # Emits file path
    file_cleared_signal = Signal()

    def __init__(self, file_type='image', parent=None):
        """Initialize image upload widget

        Args:
            file_type: 'image' or 'pdf'
            parent: Parent widget
        """
        super().__init__(parent)
        self.file_type = file_type
        self.current_file = None
        self.last_directory = os.path.expanduser("~")

        self.setup_ui()
        self.setAcceptDrops(True)

        # Install event filter for clipboard paste
        self.installEventFilter(self)

    def setup_ui(self):
        """Setup widget UI"""
        layout = QVBoxLayout()

        # Drop zone
        self.drop_zone = QLabel()
        self.drop_zone.setAlignment(Qt.AlignCenter)
        self.drop_zone.setWordWrap(True)
        self.drop_zone.setMinimumHeight(200)
        self.drop_zone.setStyleSheet("""
            QLabel {
                border: 2px dashed #888;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.05);
                padding: 40px;
                color: #aaa;
            }
            QLabel:hover {
                border-color: #0ea5e9;
                background-color: rgba(14, 165, 233, 0.1);
            }
        """)
        self.update_drop_zone_text()
        self.drop_zone.mousePressEvent = self.open_file_dialog
        layout.addWidget(self.drop_zone)

        # Preview area (initially hidden)
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setVisible(False)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setScaledContents(False)
        self.preview_scroll.setWidget(self.preview_label)
        layout.addWidget(self.preview_scroll)

        # File info label (initially hidden)
        self.file_info_label = QLabel()
        self.file_info_label.setAlignment(Qt.AlignCenter)
        self.file_info_label.setStyleSheet("color: #0ea5e9; padding: 10px;")
        self.file_info_label.setVisible(False)
        layout.addWidget(self.file_info_label)

        # Remove button (initially hidden)
        self.remove_button = QPushButton("🗑️ Remove File")
        self.remove_button.setStyleSheet("""
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
        self.remove_button.clicked.connect(self.clear_file)
        self.remove_button.setVisible(False)
        layout.addWidget(self.remove_button)

        self.setLayout(layout)

    def update_drop_zone_text(self):
        """Update drop zone text based on file type"""
        if self.file_type == 'image':
            text = (
                "📸 Drop image here or click to browse\n\n"
                "Supported: PNG, JPG, JPEG, WEBP, GIF, BMP\n"
                "Max size: 10MB\n\n"
                "💡 Press Ctrl+V to paste from clipboard"
            )
        else:  # pdf
            text = (
                "📄 Drop PDF here or click to browse\n\n"
                "Supported: PDF files\n"
                "Max size: 100MB"
            )
        self.drop_zone.setText(text)

    def set_file_type(self, file_type: str):
        """Change file type (image or pdf)

        Args:
            file_type: 'image' or 'pdf'
        """
        self.file_type = file_type
        self.update_drop_zone_text()
        self.clear_file()  # Clear current file when switching types

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event

        Args:
            event: Drag enter event
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_zone.setStyleSheet("""
                QLabel {
                    border: 2px solid #0ea5e9;
                    border-radius: 8px;
                    background-color: rgba(14, 165, 233, 0.2);
                    padding: 40px;
                    color: #0ea5e9;
                    font-weight: bold;
                }
            """)

    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        self.drop_zone.setStyleSheet("""
            QLabel {
                border: 2px dashed #888;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.05);
                padding: 40px;
                color: #aaa;
            }
            QLabel:hover {
                border-color: #0ea5e9;
                background-color: rgba(14, 165, 233, 0.1);
            }
        """)

    def dropEvent(self, event: QDropEvent):
        """Handle drop event

        Args:
            event: Drop event
        """
        self.dragLeaveEvent(None)  # Reset styling

        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.load_file(file_path)

    def open_file_dialog(self, event=None):
        """Open file dialog to select image/PDF

        Args:
            event: Mouse event (optional)
        """
        if self.file_type == 'image':
            file_filter = "Image Files (*.png *.jpg *.jpeg *.webp *.gif *.bmp);;All Files (*)"
        else:
            file_filter = "PDF Files (*.pdf);;All Files (*)"

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {self.file_type.title()}",
            self.last_directory,
            file_filter
        )

        if file_path:
            self.last_directory = os.path.dirname(file_path)
            self.load_file(file_path)

    def eventFilter(self, obj, event):
        """Event filter for clipboard paste

        Args:
            obj: Object
            event: Event

        Returns:
            True if event handled, False otherwise
        """
        if event.type() == event.Type.KeyPress and self.file_type == 'image':
            if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
                self.paste_from_clipboard()
                return True
        return super().eventFilter(obj, event)

    def paste_from_clipboard(self):
        """Paste image from clipboard"""
        from PySide6.QtWidgets import QApplication
        import tempfile

        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if mime_data.hasImage():
            image = clipboard.image()
            if not image.isNull():
                # Save to temporary file
                temp_path = os.path.join(tempfile.gettempdir(), f"pasted-image-{os.getpid()}.png")
                image.save(temp_path, 'PNG')
                self.load_file(temp_path)

    def load_file(self, file_path: str):
        """Load and display file

        Args:
            file_path: Path to file
        """
        if not os.path.exists(file_path):
            return

        # Validate file type
        ext = os.path.splitext(file_path)[1].lower()
        if self.file_type == 'image':
            valid_exts = ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp']
        else:
            valid_exts = ['.pdf']

        if ext not in valid_exts:
            return

        self.current_file = file_path

        # Hide drop zone, show preview
        self.drop_zone.setVisible(False)

        if self.file_type == 'image':
            # Load and display image preview
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale to fit while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    600, 400,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled_pixmap)
                self.preview_scroll.setVisible(True)
        else:
            # PDF: Show file icon and name
            self.preview_label.setText(f"📄 PDF File\n\n{os.path.basename(file_path)}")
            self.preview_label.setStyleSheet("font-size: 16px; color: #0ea5e9; padding: 40px;")
            self.preview_scroll.setVisible(True)

        # Show file info
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        self.file_info_label.setText(f"📁 {os.path.basename(file_path)} ({file_size:.2f} MB)")
        self.file_info_label.setVisible(True)

        # Show remove button
        self.remove_button.setVisible(True)

        # Emit signal
        self.file_selected_signal.emit(file_path)

    def clear_file(self):
        """Clear current file and reset UI"""
        self.current_file = None

        # Show drop zone, hide preview
        self.drop_zone.setVisible(True)
        self.preview_scroll.setVisible(False)
        self.file_info_label.setVisible(False)
        self.remove_button.setVisible(False)

        # Clear preview
        self.preview_label.clear()

        # Emit signal
        self.file_cleared_signal.emit()

    def get_current_file(self) -> str:
        """Get current file path

        Returns:
            Current file path or None
        """
        return self.current_file
