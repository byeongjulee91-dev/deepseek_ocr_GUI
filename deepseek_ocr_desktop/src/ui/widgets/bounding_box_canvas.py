"""
Bounding Box Canvas
Custom QLabel widget that renders bounding boxes using QPainter
Adapted from frontend/src/components/ResultPanel.jsx drawBoxes() function
"""

from typing import List, Dict, Any, Optional
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QFont


class BoundingBoxCanvas(QLabel):
    """Custom label that renders image with bounding box overlays"""

    def __init__(self, parent=None):
        """Initialize bounding box canvas

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.image_pixmap = None
        self.boxes = []  # List of {label, box: [x1,y1,x2,y2]}
        self.image_dims = None  # Original image dimensions {w, h}

        # Colors for bounding boxes (matching frontend)
        self.colors = [
            QColor(0, 255, 0),      # Green
            QColor(0, 255, 255),    # Cyan
            QColor(255, 0, 255),    # Magenta
            QColor(255, 255, 0),    # Yellow
            QColor(255, 0, 102),    # Pink
        ]

        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(False)

    def set_image_and_boxes(self, image_path: str, boxes: List[Dict[str, Any]], image_dims: Dict[str, int]):
        """Set image and bounding boxes to display

        Args:
            image_path: Path to image file
            boxes: List of bounding boxes with format [{"label": str, "box": [x1,y1,x2,y2]}]
            image_dims: Original image dimensions {"w": width, "h": height}
        """
        # Load image
        self.image_pixmap = QPixmap(image_path)
        self.boxes = boxes
        self.image_dims = image_dims

        # Display image
        if not self.image_pixmap.isNull():
            # Scale to fit while maintaining aspect ratio
            scaled_pixmap = self.image_pixmap.scaled(
                800, 600,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)

        # Trigger repaint
        self.update()

    def clear_boxes(self):
        """Clear all bounding boxes"""
        self.boxes = []
        self.update()

    def paintEvent(self, event):
        """Paint event to draw image and bounding boxes

        Args:
            event: Paint event
        """
        # Call parent to draw the pixmap first
        super().paintEvent(event)

        # Don't draw boxes if no image or no boxes
        if not self.pixmap() or not self.boxes or not self.image_dims:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get display size vs original image size for scaling
        display_width = self.pixmap().width()
        display_height = self.pixmap().height()
        original_width = self.image_dims.get('w', 1)
        original_height = self.image_dims.get('h', 1)

        # Calculate scaling factors
        scale_x = display_width / original_width
        scale_y = display_height / original_height

        # Calculate offset (image is centered)
        offset_x = (self.width() - display_width) // 2
        offset_y = (self.height() - display_height) // 2

        # Draw each bounding box
        for idx, box_data in enumerate(self.boxes):
            label = box_data.get('label', 'unknown')
            box = box_data.get('box', [])

            if len(box) < 4:
                continue

            x1, y1, x2, y2 = box

            # Scale coordinates to display size
            sx = int(x1 * scale_x) + offset_x
            sy = int(y1 * scale_y) + offset_y
            sw = int((x2 - x1) * scale_x)
            sh = int((y2 - y1) * scale_y)

            # Get color (cycle through colors)
            color = self.colors[idx % len(self.colors)]

            # Draw semi-transparent fill
            fill_color = QColor(color)
            fill_color.setAlpha(51)  # 20% opacity (51/255)
            painter.setBrush(QBrush(fill_color))
            painter.setPen(Qt.NoPen)
            painter.drawRect(sx, sy, sw, sh)

            # Draw thick border with glow effect
            pen = QPen(color, 4)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(sx, sy, sw, sh)

            # Draw label background
            label_padding = 4
            label_font = QFont("Arial", 12, QFont.Bold)
            painter.setFont(label_font)

            # Calculate label size
            label_metrics = painter.fontMetrics()
            label_width = label_metrics.horizontalAdvance(label) + label_padding * 2
            label_height = label_metrics.height() + label_padding

            # Label position (above box)
            label_x = sx
            label_y = sy - label_height

            # If label would go off top, draw inside box
            if label_y < offset_y:
                label_y = sy

            # Draw label background
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawRect(label_x, label_y, label_width, label_height)

            # Draw label text
            painter.setPen(QPen(Qt.white))
            painter.drawText(
                label_x + label_padding,
                label_y + label_metrics.ascent() + label_padding // 2,
                label
            )


class ImageWithBoxesWidget(QWidget):
    """Widget that contains scrollable image canvas with bounding boxes"""

    def __init__(self, parent=None):
        """Initialize image with boxes widget

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup widget UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for large images
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)

        # Canvas
        self.canvas = BoundingBoxCanvas()
        self.scroll_area.setWidget(self.canvas)

        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

    def display_image_with_boxes(self, image_path: str, boxes: List[Dict[str, Any]], image_dims: Dict[str, int]):
        """Display image with bounding boxes

        Args:
            image_path: Path to image file
            boxes: List of bounding boxes
            image_dims: Original image dimensions
        """
        self.canvas.set_image_and_boxes(image_path, boxes, image_dims)

    def clear(self):
        """Clear display"""
        self.canvas.clear()
        self.canvas.setPixmap(QPixmap())  # Clear image
