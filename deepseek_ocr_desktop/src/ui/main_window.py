"""
Main Window for DeepSeek OCR Desktop Application
QSplitter-based layout with left control panel and right result viewer
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QLabel, QStatusBar, QMenuBar, QMenu, QPushButton,
    QButtonGroup, QRadioButton
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction

# Import widgets
from .widgets.image_upload_widget import ImageUploadWidget
from .widgets.result_viewer_widget import ResultViewerWidget
from .widgets.mode_selector_widget import ModeSelectorWidget
from .widgets.pdf_processor_widget import PDFProcessorWidget
from .widgets.advanced_settings_widget import AdvancedSettingsWidget
from .widgets.log_viewer_widget import LogViewerWidget

# Import dialogs
from .dialogs.settings_dialog import SettingsDialog

# Import core components
from ..core.ocr_processor import OCRProcessor
from ..core.pdf_processor import PDFProcessor

# Import logging utilities
from ..utils.qt_log_handler import get_qt_log_handler, attach_qt_handler_to_logger


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, model_manager, config):
        """Initialize main window

        Args:
            model_manager: ModelManager instance with loaded model
            config: AppConfig instance for settings
        """
        super().__init__()
        self.model_manager = model_manager
        self.config = config

        # Application state
        self.current_file = None
        self.current_mode = "plain_ocr"
        self.file_type = "image"  # "image" or "pdf"
        self.find_term = ""
        self.custom_prompt = ""

        # Create OCR processor
        self.ocr_processor = OCRProcessor(
            model_manager.get_model(),
            model_manager.get_tokenizer()
        )

        # Create PDF processor
        self.pdf_processor = PDFProcessor(
            model_manager.get_model(),
            model_manager.get_tokenizer()
        )

        # Log viewer (will be created in setup_ui)
        self.log_viewer = None

        self.setup_ui()
        self.setup_logging()
        self.restore_geometry()

    def setup_ui(self):
        """Setup main window UI"""
        self.setWindowTitle("DeepSeek-OCR Desktop")
        self.setMinimumSize(QSize(1200, 800))

        # Create central widget with splitter
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create horizontal splitter
        self.splitter = QSplitter(Qt.Horizontal)

        # Left panel (control panel)
        self.left_panel = self.create_left_panel()
        self.splitter.addWidget(self.left_panel)

        # Right panel (result viewer)
        self.right_panel = self.create_right_panel()
        self.splitter.addWidget(self.right_panel)

        # Set initial splitter sizes (40% left, 60% right)
        self.splitter.setSizes([400, 600])

        main_layout.addWidget(self.splitter)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Create menu bar
        self.create_menu_bar()

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✅ Model loaded. Ready to process images!")

    def create_left_panel(self) -> QWidget:
        """Create left control panel

        Returns:
            QWidget for left panel
        """
        panel = QWidget()
        layout = QVBoxLayout()

        # Get UI font size from config
        ui_font_size = self.config.get_ui_font_size()

        # Title
        self.control_panel_title = QLabel("📋 Control Panel")
        self.control_panel_title.setStyleSheet(f"font-size: {ui_font_size + 4}px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.control_panel_title)

        # File type toggle (Image / PDF)
        file_type_widget = QWidget()
        file_type_layout = QHBoxLayout()
        file_type_layout.setContentsMargins(10, 5, 10, 5)

        self.file_type_group = QButtonGroup()

        self.image_radio = QRadioButton("📸 Image")
        self.image_radio.setChecked(True)
        self.image_radio.setStyleSheet(f"font-size: {ui_font_size}px;")
        self.image_radio.toggled.connect(lambda checked: self.on_file_type_changed('image') if checked else None)
        self.file_type_group.addButton(self.image_radio)
        file_type_layout.addWidget(self.image_radio)

        self.pdf_radio = QRadioButton("📄 PDF")
        self.pdf_radio.setStyleSheet(f"font-size: {ui_font_size}px;")
        self.pdf_radio.toggled.connect(lambda checked: self.on_file_type_changed('pdf') if checked else None)
        self.file_type_group.addButton(self.pdf_radio)
        file_type_layout.addWidget(self.pdf_radio)

        file_type_widget.setLayout(file_type_layout)
        layout.addWidget(file_type_widget)

        # File upload widget (supports both image and PDF)
        self.image_upload = ImageUploadWidget(file_type='image')
        self.image_upload.file_selected_signal.connect(self.on_file_selected)
        self.image_upload.file_cleared_signal.connect(self.on_file_cleared)
        layout.addWidget(self.image_upload)

        # Mode selector widget (for images)
        self.mode_selector = ModeSelectorWidget()
        self.mode_selector.mode_changed_signal.connect(self.on_mode_changed)
        self.mode_selector.find_term_changed_signal.connect(self.on_find_term_changed)
        self.mode_selector.prompt_changed_signal.connect(self.on_prompt_changed)
        layout.addWidget(self.mode_selector)

        # PDF processor widget (for PDFs, initially hidden)
        self.pdf_processor_widget = PDFProcessorWidget()
        self.pdf_processor_widget.setVisible(False)
        layout.addWidget(self.pdf_processor_widget)

        # Advanced settings widget
        self.advanced_settings = AdvancedSettingsWidget(self.config)
        layout.addWidget(self.advanced_settings)

        # Analyze/Process button
        self.analyze_button = QPushButton("🔍 Analyze Image")
        self.analyze_button.setEnabled(False)
        self.analyze_button.setMinimumHeight(50)
        self._apply_analyze_button_style(ui_font_size)
        self.analyze_button.clicked.connect(self.handle_analyze_clicked)
        layout.addWidget(self.analyze_button)

        # Cancel button (for PDF processing, initially hidden)
        self.cancel_button = QPushButton("⏹️ Cancel Processing")
        self.cancel_button.setVisible(False)
        self.cancel_button.setMinimumHeight(40)
        self._apply_cancel_button_style(ui_font_size)
        self.cancel_button.clicked.connect(self.handle_cancel_clicked)
        layout.addWidget(self.cancel_button)

        # Info label
        self.info_label = QLabel("ℹ️ Upload an image to begin OCR processing")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet(f"padding: 10px; color: gray; font-size: {ui_font_size - 1}px;")
        layout.addWidget(self.info_label)

        layout.addStretch()
        panel.setLayout(layout)

        return panel

    def create_right_panel(self) -> QWidget:
        """Create right result viewer panel

        Returns:
            QWidget for right panel
        """
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create vertical splitter for result viewer and log viewer
        self.right_splitter = QSplitter(Qt.Vertical)

        # Top: Result viewer
        result_container = QWidget()
        result_layout = QVBoxLayout()
        result_layout.setContentsMargins(0, 0, 0, 0)

        ui_font_size = self.config.get_ui_font_size()
        self.result_title = QLabel("📊 Result Viewer")
        self.result_title.setStyleSheet(f"font-size: {ui_font_size + 4}px; font-weight: bold; padding: 10px;")
        result_layout.addWidget(self.result_title)

        self.result_viewer = ResultViewerWidget(config=self.config)
        result_layout.addWidget(self.result_viewer)

        result_container.setLayout(result_layout)
        self.right_splitter.addWidget(result_container)

        # Bottom: Log viewer
        log_container = QWidget()
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(0, 0, 0, 0)

        self.log_title = QLabel("📋 Application Logs")
        self.log_title.setStyleSheet(f"font-size: {ui_font_size + 4}px; font-weight: bold; padding: 10px;")
        log_layout.addWidget(self.log_title)

        self.log_viewer = LogViewerWidget(config=self.config)
        log_layout.addWidget(self.log_viewer)

        log_container.setLayout(log_layout)
        self.right_splitter.addWidget(log_container)

        # Set initial sizes (70% result, 30% logs)
        self.right_splitter.setSizes([700, 300])

        layout.addWidget(self.right_splitter)
        panel.setLayout(layout)

        return panel

    def setup_logging(self):
        """Setup logging connection to GUI log viewer"""
        # Attach Qt log handler to the root logger
        attach_qt_handler_to_logger("DeepSeekOCR")

        # Get the Qt log handler
        qt_handler = get_qt_log_handler()

        # Connect the log signal to the log viewer
        if self.log_viewer:
            qt_handler.log_signal.connect(self.log_viewer.append_log)

    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Open action
        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open image or PDF file")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        # Copy action
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.setStatusTip("Copy result to clipboard")
        copy_action.triggered.connect(self.copy_result)
        edit_menu.addAction(copy_action)

        # Settings action
        settings_action = QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.setStatusTip("Open settings")
        settings_action.triggered.connect(self.open_settings)
        edit_menu.addAction(settings_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        # Toggle log viewer
        self.toggle_logs_action = QAction("&Show Logs", self)
        self.toggle_logs_action.setCheckable(True)
        self.toggle_logs_action.setChecked(True)
        self.toggle_logs_action.setShortcut("Ctrl+L")
        self.toggle_logs_action.setStatusTip("Toggle log viewer")
        self.toggle_logs_action.triggered.connect(self.toggle_log_viewer)
        view_menu.addAction(self.toggle_logs_action)

        # Toggle advanced settings
        toggle_advanced = QAction("&Advanced Settings", self)
        toggle_advanced.setCheckable(True)
        toggle_advanced.setChecked(True)
        toggle_advanced.setStatusTip("Toggle advanced settings panel")
        # toggle_advanced.triggered.connect(self.toggle_advanced_settings)  # Will implement in Phase 2
        view_menu.addAction(toggle_advanced)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        # Keyboard shortcuts action
        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.setShortcut("F1")
        shortcuts_action.setStatusTip("Show keyboard shortcuts")
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)

        help_menu.addSeparator()

        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("About DeepSeek-OCR Desktop")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Setup additional keyboard shortcuts
        self.setup_shortcuts()

    def setup_shortcuts(self):
        """Setup additional keyboard shortcuts"""
        from PySide6.QtGui import QShortcut, QKeySequence

        # F5 - Process/Analyze
        process_shortcut = QShortcut(QKeySequence("F5"), self)
        process_shortcut.activated.connect(self.handle_analyze_clicked)

        # Escape - Clear file
        clear_shortcut = QShortcut(QKeySequence("Escape"), self)
        clear_shortcut.activated.connect(self.clear_current_file)

        # Ctrl+T - Toggle file type
        toggle_type_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        toggle_type_shortcut.activated.connect(self.toggle_file_type)

        # Ctrl+Shift+S - Save result
        save_shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        save_shortcut.activated.connect(self.save_result)

    def show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Keyboard Shortcuts",
            "<h3>Keyboard Shortcuts</h3>"
            "<p><b>File Operations:</b></p>"
            "<ul>"
            "<li><b>Ctrl+O</b> - Open file</li>"
            "<li><b>Ctrl+T</b> - Toggle between Image/PDF mode</li>"
            "<li><b>Escape</b> - Clear current file</li>"
            "</ul>"
            "<p><b>Processing:</b></p>"
            "<ul>"
            "<li><b>F5</b> - Start processing (Analyze/Process)</li>"
            "</ul>"
            "<p><b>Results:</b></p>"
            "<ul>"
            "<li><b>Ctrl+C</b> - Copy result to clipboard</li>"
            "<li><b>Ctrl+Shift+S</b> - Save result to file</li>"
            "</ul>"
            "<p><b>View:</b></p>"
            "<ul>"
            "<li><b>Ctrl+L</b> - Toggle log viewer</li>"
            "</ul>"
            "<p><b>Application:</b></p>"
            "<ul>"
            "<li><b>Ctrl+,</b> - Open settings</li>"
            "<li><b>F1</b> - Show keyboard shortcuts</li>"
            "<li><b>Ctrl+Q</b> - Exit application</li>"
            "</ul>"
        )

    def show_about(self):
        """Show about dialog"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "About DeepSeek-OCR Desktop",
            "<h2>DeepSeek-OCR Desktop</h2>"
            "<p><b>Version:</b> 1.0.0 (Phase 5)</p>"
            "<p><b>Model:</b> deepseek-ai/DeepSeek-OCR</p>"
            "<p>A powerful desktop application for OCR and PDF processing.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>4 OCR modes for images</li>"
            "<li>Multi-page PDF processing</li>"
            "<li>Export to Markdown, HTML, DOCX, JSON</li>"
            "<li>Bounding box visualization</li>"
            "<li>Advanced settings & customization</li>"
            "</ul>"
            "<p>Built with PySide6 and PyTorch.</p>"
            "<p><i>Press F1 for keyboard shortcuts</i></p>"
        )

    # Signal handlers
    def on_file_type_changed(self, file_type: str):
        """Handle file type changed (image/pdf)

        Args:
            file_type: New file type ('image' or 'pdf')
        """
        self.file_type = file_type

        # Update upload widget
        self.image_upload.set_file_type(file_type)

        # Show/hide appropriate widgets
        if file_type == 'image':
            self.mode_selector.setVisible(True)
            self.pdf_processor_widget.setVisible(False)
            self.analyze_button.setText("🔍 Analyze Image")
            self.status_bar.showMessage("✅ Ready to process images")
        else:  # pdf
            self.mode_selector.setVisible(False)
            self.pdf_processor_widget.setVisible(True)
            self.pdf_processor_widget.reset_progress()
            self.analyze_button.setText("📄 Process PDF")
            self.status_bar.showMessage("✅ Ready to process PDFs")

        # Clear result viewer
        self.result_viewer.clear()

    def on_file_selected(self, file_path: str):
        """Handle file selected event

        Args:
            file_path: Path to selected file
        """
        self.current_file = file_path
        self.analyze_button.setEnabled(True)

        file_type_str = "image" if self.file_type == "image" else "PDF"
        self.status_bar.showMessage(f"📁 {file_type_str} loaded: {file_path}")

    def on_file_cleared(self):
        """Handle file cleared event"""
        self.current_file = None
        self.analyze_button.setEnabled(False)
        self.result_viewer.clear()

        if self.file_type == "pdf":
            self.pdf_processor_widget.reset_progress()

        file_type_str = "images" if self.file_type == "image" else "PDFs"
        self.status_bar.showMessage(f"Ready to process {file_type_str}")

    def on_mode_changed(self, mode: str):
        """Handle OCR mode changed

        Args:
            mode: New mode identifier
        """
        self.current_mode = mode
        self.status_bar.showMessage(f"Mode changed to: {mode}")

    def on_find_term_changed(self, term: str):
        """Handle find term changed

        Args:
            term: Find term text
        """
        self.find_term = term

    def on_prompt_changed(self, prompt: str):
        """Handle custom prompt changed

        Args:
            prompt: Custom prompt text
        """
        self.custom_prompt = prompt

    def handle_analyze_clicked(self):
        """Handle analyze/process button click"""
        if not self.current_file:
            return

        if self.file_type == 'image':
            self.start_image_processing()
        else:  # pdf
            self.start_pdf_processing()

    def handle_cancel_clicked(self):
        """Handle cancel button click"""
        if self.file_type == 'pdf':
            self.pdf_processor.cancel_current()
            self.status_bar.showMessage("❌ PDF processing cancelled")
            self.cancel_button.setVisible(False)
            self.analyze_button.setEnabled(True)
            self.analyze_button.setText("📄 Process PDF")

    def start_image_processing(self):
        """Start image OCR processing"""
        # Disable button during processing
        self.analyze_button.setEnabled(False)
        self.analyze_button.setText("⏳ Processing...")

        # Show loading state
        self.result_viewer.show_loading()
        self.status_bar.showMessage("🔍 Running OCR inference...")

        # Collect parameters
        params = {
            'mode': self.current_mode,
            'prompt': self.custom_prompt if self.current_mode == 'freeform' else '',
            'grounding': self.mode_selector.has_grounding(),
            'find_term': self.find_term if self.current_mode == 'find_ref' else None,
            'schema': None,
            'include_caption': self.config.get_include_caption(),
            'base_size': self.config.get_base_size(),
            'image_size': self.config.get_image_size(),
            'crop_mode': self.config.get_crop_mode(),
            'test_compress': self.config.get_test_compress(),
        }

        # Create and start OCR worker
        worker = self.ocr_processor.process_image(self.current_file, params)

        # Connect worker signals
        worker.progress_signal.connect(self.on_ocr_progress)
        worker.result_signal.connect(self.on_ocr_result)
        worker.error_signal.connect(self.on_ocr_error)

        # Start processing
        worker.start()

    def start_pdf_processing(self):
        """Start PDF processing"""
        # Disable button, show cancel button
        self.analyze_button.setEnabled(False)
        self.analyze_button.setText("⏳ Processing PDF...")
        self.cancel_button.setVisible(True)

        # Reset progress
        self.pdf_processor_widget.reset_progress()

        # Show loading state
        self.result_viewer.show_loading()
        self.status_bar.showMessage("📄 Processing PDF...")

        # Collect parameters
        params = {
            'output_format': self.pdf_processor_widget.get_selected_format(),
            'dpi': self.pdf_processor_widget.get_dpi(),
            'extract_images': self.pdf_processor_widget.get_extract_images(),
            'include_caption': self.config.get_include_caption(),
            'base_size': self.config.get_base_size(),
            'image_size': self.config.get_image_size(),
            'crop_mode': self.config.get_crop_mode(),
            'test_compress': self.config.get_test_compress(),
        }

        # Create and start PDF worker
        worker = self.pdf_processor.process_pdf(self.current_file, params)

        # Connect worker signals
        worker.page_progress_signal.connect(self.on_pdf_page_progress)
        worker.page_complete_signal.connect(self.on_pdf_page_complete)
        worker.finished_signal.connect(self.on_pdf_finished)
        worker.error_signal.connect(self.on_pdf_error)
        worker.status_signal.connect(self.on_pdf_status)

        # Start processing
        worker.start()

    def on_ocr_progress(self, message: str):
        """Handle OCR progress update

        Args:
            message: Progress message
        """
        self.status_bar.showMessage(message)

    def on_ocr_result(self, result: dict):
        """Handle OCR result

        Args:
            result: OCR result dict
        """
        # Display result (pass image path for bounding box display)
        self.result_viewer.display_result(result, self.current_file)

        # Re-enable button
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("🔍 Analyze Image")

        # Update status bar
        text_length = len(result.get('text', ''))
        boxes_count = len(result.get('boxes', []))
        self.status_bar.showMessage(
            f"✅ OCR complete! Extracted {text_length} characters, {boxes_count} bounding boxes"
        )

    def on_ocr_error(self, error_message: str):
        """Handle OCR error

        Args:
            error_message: Error message
        """
        from PySide6.QtWidgets import QMessageBox

        # Show error in result viewer
        self.result_viewer.show_error(error_message)

        # Show error dialog
        QMessageBox.critical(
            self,
            "OCR Error",
            f"Failed to process image:\n\n{error_message}"
        )

        # Re-enable button
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("🔍 Analyze Image")

        self.status_bar.showMessage("❌ OCR failed")

    def on_pdf_page_progress(self, current_page: int, total_pages: int):
        """Handle PDF page progress update

        Args:
            current_page: Current page number (1-indexed)
            total_pages: Total number of pages
        """
        self.pdf_processor_widget.update_progress(current_page, total_pages)

    def on_pdf_page_complete(self, page_num: int, page_result: dict):
        """Handle PDF page completion

        Args:
            page_num: Completed page number
            page_result: Page processing result
        """
        text_length = len(page_result.get('text', ''))
        boxes_count = len(page_result.get('boxes', []))
        detail = f"Extracted {text_length} chars, {boxes_count} boxes"
        self.pdf_processor_widget.add_page_detail(page_num, detail)

    def on_pdf_finished(self, result: dict):
        """Handle PDF processing completion

        Args:
            result: Final processing result
        """
        # Show completion in PDF widget
        self.pdf_processor_widget.show_complete(result)

        # Display result in result viewer
        content = result.get('content', '')
        format_name = result.get('format', 'text')

        # For text formats, display in result viewer
        if format_name in ['markdown', 'html', 'json']:
            display_result = {
                'text': content,
                'raw_text': content,
                'boxes': [],
                'metadata': {
                    'format': format_name,
                    'total_pages': result.get('total_pages', 0),
                    'extracted_images': result.get('extracted_images_count', 0)
                }
            }
            self.result_viewer.display_result(display_result)
        else:
            # For binary formats (docx), show success message
            self.result_viewer.display_result({
                'text': f"✅ PDF processed successfully!\n\n"
                        f"Format: {format_name.upper()}\n"
                        f"Total pages: {result.get('total_pages', 0)}\n\n"
                        f"Click 'Save Document' button to download.",
                'raw_text': '',
                'boxes': [],
                'metadata': result.get('metadata', {})
            })

        # Re-enable button, hide cancel button
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("📄 Process PDF")
        self.cancel_button.setVisible(False)

        # Update status bar
        total_pages = result.get('total_pages', 0)
        self.status_bar.showMessage(f"✅ PDF processing complete! {total_pages} pages processed.")

    def on_pdf_error(self, error_message: str):
        """Handle PDF processing error

        Args:
            error_message: Error message
        """
        from PySide6.QtWidgets import QMessageBox

        # Show error in PDF widget
        self.pdf_processor_widget.show_error(error_message)

        # Show error in result viewer
        self.result_viewer.show_error(error_message)

        # Show error dialog
        QMessageBox.critical(
            self,
            "PDF Processing Error",
            f"Failed to process PDF:\n\n{error_message}"
        )

        # Re-enable button, hide cancel button
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("📄 Process PDF")
        self.cancel_button.setVisible(False)

        self.status_bar.showMessage("❌ PDF processing failed")

    def on_pdf_status(self, message: str):
        """Handle PDF status update

        Args:
            message: Status message
        """
        self.pdf_processor_widget.update_status(message)
        self.status_bar.showMessage(message)

    def open_file(self):
        """Handle Open menu action"""
        from PySide6.QtWidgets import QFileDialog

        # Determine filter based on current file type
        if self.file_type == 'image':
            file_filter = "Image Files (*.png *.jpg *.jpeg *.webp *.gif *.bmp);;All Files (*)"
            title = "Open Image"
        else:
            file_filter = "PDF Files (*.pdf);;All Files (*)"
            title = "Open PDF"

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            title,
            "",
            file_filter
        )

        if file_path:
            self.image_upload.load_file(file_path)

    def copy_result(self):
        """Handle Copy menu action"""
        # Delegate to result viewer's copy function
        if self.result_viewer.current_result:
            self.result_viewer.copy_to_clipboard()
        else:
            self.status_bar.showMessage("No result to copy")

    def open_settings(self):
        """Handle Settings menu action"""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            # Settings were saved, reload advanced settings
            self.advanced_settings.load_settings()

            # Refresh font settings in viewers
            self.result_viewer.refresh_settings()
            self.log_viewer.refresh_settings()

            # Refresh UI font sizes
            self.refresh_ui_font_size()

            self.status_bar.showMessage("Settings updated")

    def clear_current_file(self):
        """Clear current file (Escape shortcut)"""
        if self.current_file:
            self.image_upload.clear_file()
            self.status_bar.showMessage("File cleared")

    def toggle_file_type(self):
        """Toggle between Image and PDF mode (Ctrl+T shortcut)"""
        if self.file_type == 'image':
            self.pdf_radio.setChecked(True)
        else:
            self.image_radio.setChecked(True)

    def save_result(self):
        """Save result to file (Ctrl+Shift+S shortcut)"""
        if self.file_type == 'pdf' and self.pdf_processor_widget.current_result:
            # PDF result - delegate to PDF widget's download button
            self.pdf_processor_widget.on_download_clicked()
        elif self.result_viewer.current_result:
            # Image result - delegate to result viewer's download button
            self.result_viewer.download_result()
        else:
            self.status_bar.showMessage("No result to save")

    def toggle_log_viewer(self, checked: bool):
        """Toggle log viewer visibility (Ctrl+L shortcut)"""
        if self.log_viewer:
            # Get the log container (parent of log viewer)
            log_container = self.right_splitter.widget(1)
            if log_container:
                log_container.setVisible(checked)

            # Update menu action text
            self.toggle_logs_action.setText("Hide Logs" if checked else "Show Logs")

            # Update status bar
            status = "shown" if checked else "hidden"
            self.status_bar.showMessage(f"Log viewer {status}")

    def _apply_analyze_button_style(self, font_size: int):
        """Apply style to analyze button with given font size"""
        self.analyze_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #9333ea, stop:1 #06b6d4);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: {font_size + 2}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #7c3aed, stop:1 #0891b2);
            }}
            QPushButton:disabled {{
                background: #555;
                color: #888;
            }}
        """)

    def _apply_cancel_button_style(self, font_size: int):
        """Apply style to cancel button with given font size"""
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: {font_size}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #dc2626;
            }}
        """)

    def refresh_ui_font_size(self):
        """Refresh UI font sizes from config"""
        ui_font_size = self.config.get_ui_font_size()

        # Update Control Panel title
        self.control_panel_title.setStyleSheet(f"font-size: {ui_font_size + 4}px; font-weight: bold; padding: 10px;")

        # Update radio buttons
        self.image_radio.setStyleSheet(f"font-size: {ui_font_size}px;")
        self.pdf_radio.setStyleSheet(f"font-size: {ui_font_size}px;")

        # Update buttons
        self._apply_analyze_button_style(ui_font_size)
        self._apply_cancel_button_style(ui_font_size)

        # Update info label
        self.info_label.setStyleSheet(f"padding: 10px; color: gray; font-size: {ui_font_size - 1}px;")

        # Update Result Viewer and Log Viewer titles
        self.result_title.setStyleSheet(f"font-size: {ui_font_size + 4}px; font-weight: bold; padding: 10px;")
        self.log_title.setStyleSheet(f"font-size: {ui_font_size + 4}px; font-weight: bold; padding: 10px;")

    def restore_geometry(self):
        """Restore saved window geometry and state"""
        geometry = self.config.get_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)

        state = self.config.get_window_state()
        if state:
            self.restoreState(state)

        splitter_state = self.config.get_splitter_state()
        if splitter_state:
            self.splitter.restoreState(splitter_state)

    def closeEvent(self, event):
        """Handle window close event

        Args:
            event: Close event
        """
        # Save window geometry and state
        self.config.set_window_geometry(self.saveGeometry())
        self.config.set_window_state(self.saveState())
        self.config.set_splitter_state(self.splitter.saveState())
        self.config.sync()

        event.accept()
