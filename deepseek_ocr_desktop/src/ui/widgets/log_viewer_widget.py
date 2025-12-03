"""
Log Viewer Widget
Real-time log display with color coding and filtering
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QComboBox, QLabel, QCheckBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QTextCursor, QColor, QTextCharFormat
import logging


class LogViewerWidget(QWidget):
    """Widget for displaying application logs in real-time"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

        # Log level colors
        self.level_colors = {
            'DEBUG': QColor(150, 150, 150),    # Gray
            'INFO': QColor(100, 200, 100),     # Green
            'WARNING': QColor(255, 165, 0),    # Orange
            'ERROR': QColor(255, 100, 100),    # Red
            'CRITICAL': QColor(255, 0, 255)    # Magenta
        }

        # Current filter level
        self.filter_level = logging.DEBUG

    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        toolbar = QHBoxLayout()

        # Level filter
        toolbar.addWidget(QLabel("Filter:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(['ALL', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
        self.level_combo.setCurrentText('INFO')
        self.level_combo.currentTextChanged.connect(self.on_filter_changed)
        toolbar.addWidget(self.level_combo)

        toolbar.addStretch()

        # Auto-scroll checkbox
        self.autoscroll_check = QCheckBox("Auto-scroll")
        self.autoscroll_check.setChecked(True)
        toolbar.addWidget(self.autoscroll_check)

        # Clear button
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_logs)
        toolbar.addWidget(self.clear_btn)

        # Copy button
        self.copy_btn = QPushButton("📋 Copy All")
        self.copy_btn.clicked.connect(self.copy_all_logs)
        toolbar.addWidget(self.copy_btn)

        # Export button
        self.export_btn = QPushButton("💾 Export")
        self.export_btn.clicked.connect(self.export_logs)
        toolbar.addWidget(self.export_btn)

        layout.addLayout(toolbar)

        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                border: 1px solid #3c3c3c;
                padding: 5px;
            }
        """)
        layout.addWidget(self.log_text)

        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #888; font-size: 10px;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        self.line_count_label = QLabel("0 lines")
        self.line_count_label.setStyleSheet("color: #888; font-size: 10px;")
        status_layout.addWidget(self.line_count_label)
        layout.addLayout(status_layout)

    def on_filter_changed(self, level_text: str):
        """Handle filter level change"""
        level_map = {
            'ALL': logging.DEBUG,
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        self.filter_level = level_map.get(level_text, logging.DEBUG)
        self.status_label.setText(f"Filter: {level_text}")

    @Slot(str, str)
    def append_log(self, level: str, message: str):
        """
        Append a log message to the viewer

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
        """
        # Check filter
        level_num_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        if level_num_map.get(level, logging.DEBUG) < self.filter_level:
            return

        # Get cursor
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Format for level
        level_format = QTextCharFormat()
        level_color = self.level_colors.get(level, QColor(200, 200, 200))
        level_format.setForeground(level_color)
        level_format.setFontWeight(700)  # Bold

        # Format for message
        message_format = QTextCharFormat()
        message_format.setForeground(QColor(212, 212, 212))

        # Insert level
        cursor.insertText(f"[{level:8s}] ", level_format)

        # Insert message
        cursor.insertText(message + "\n", message_format)

        # Auto-scroll
        if self.autoscroll_check.isChecked():
            self.log_text.setTextCursor(cursor)
            self.log_text.ensureCursorVisible()

        # Update line count
        line_count = self.log_text.document().lineCount()
        self.line_count_label.setText(f"{line_count} lines")

    def clear_logs(self):
        """Clear all logs"""
        self.log_text.clear()
        self.line_count_label.setText("0 lines")
        self.status_label.setText("Logs cleared")

    def copy_all_logs(self):
        """Copy all logs to clipboard"""
        from PySide6.QtWidgets import QApplication
        text = self.log_text.toPlainText()
        QApplication.clipboard().setText(text)
        self.status_label.setText(f"Copied {len(text)} characters to clipboard")

    def export_logs(self):
        """Export logs to file"""
        from PySide6.QtWidgets import QFileDialog
        from datetime import datetime

        default_name = f"deepseek_ocr_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            default_name,
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                self.status_label.setText(f"Exported to: {file_path}")
            except Exception as e:
                self.status_label.setText(f"Export failed: {e}")

    def get_log_count(self) -> int:
        """Get number of log lines"""
        return self.log_text.document().lineCount()
