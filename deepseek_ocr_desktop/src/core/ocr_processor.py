"""
OCR Processor
QThread worker for running OCR inference in background
Adapted from backend/main.py /api/ocr endpoint (lines 258-386)
"""

import os
import tempfile
import shutil
from typing import Optional
from PySide6.QtCore import QThread, Signal
from PIL import Image

from .prompt_builder import build_prompt
from .coordinate_parser import parse_detections, clean_grounding_text


class OCRWorker(QThread):
    """Worker thread for OCR inference"""

    progress_signal = Signal(str)  # Progress message
    result_signal = Signal(dict)   # OCR result dict
    error_signal = Signal(str)     # Error message

    def __init__(self, model, tokenizer, image_path: str, params: dict):
        """Initialize OCR worker

        Args:
            model: DeepSeek-OCR model
            tokenizer: Model tokenizer
            image_path: Path to image file
            params: Processing parameters dict with keys:
                - mode: OCR mode
                - prompt: Custom prompt (for freeform)
                - grounding: Enable grounding boxes
                - find_term: Term to find (for find_ref)
                - schema: JSON schema (for kv_json)
                - include_caption: Add image caption
                - base_size: Base processing size
                - image_size: Image size parameter
                - crop_mode: Enable crop mode
                - test_compress: Test compression
        """
        super().__init__()
        self.model = model
        self.tokenizer = tokenizer
        self.image_path = image_path
        self.params = params

    def run(self):
        """Run OCR inference (executes in background thread)"""
        tmp_img = None
        out_dir = None

        try:
            self.progress_signal.emit("📋 Building prompt...")

            # Build prompt based on mode
            prompt_text = build_prompt(
                mode=self.params.get('mode', 'plain_ocr'),
                user_prompt=self.params.get('prompt', ''),
                grounding=self.params.get('grounding', False),
                find_term=self.params.get('find_term', None),
                schema=self.params.get('schema', None),
                include_caption=self.params.get('include_caption', False),
            )

            self.progress_signal.emit("📐 Getting image dimensions...")

            # Get original image dimensions for coordinate scaling
            try:
                with Image.open(self.image_path) as im:
                    orig_w, orig_h = im.size
            except Exception:
                orig_w = orig_h = None

            # Create temporary output directory
            out_dir = tempfile.mkdtemp(prefix="dsocr_")

            self.progress_signal.emit("🔍 Running OCR inference (this may take 10-30 seconds)...")

            # Run model inference (blocking call)
            res = self.model.infer(
                self.tokenizer,
                prompt=prompt_text,
                image_file=self.image_path,
                output_path=out_dir,
                base_size=self.params.get('base_size', 1024),
                image_size=self.params.get('image_size', 640),
                crop_mode=self.params.get('crop_mode', True),
                save_results=False,
                test_compress=self.params.get('test_compress', False),
                eval_mode=True,
            )

            self.progress_signal.emit("📊 Processing results...")

            # Normalize response
            if isinstance(res, str):
                text = res.strip()
            elif isinstance(res, dict) and "text" in res:
                text = str(res["text"]).strip()
            elif isinstance(res, (list, tuple)):
                text = "\n".join(map(str, res)).strip()
            else:
                text = ""

            # Fallback: check output file
            if not text:
                mmd = os.path.join(out_dir, "result.mmd")
                if os.path.exists(mmd):
                    with open(mmd, "r", encoding="utf-8") as fh:
                        text = fh.read().strip()
            if not text:
                text = "No text returned by model."

            # Parse grounding boxes with proper coordinate scaling
            boxes = []
            if ("<|det|>" in text or "<|ref|>" in text) and orig_w and orig_h:
                boxes = parse_detections(text, orig_w, orig_h)

            # Clean grounding tags from display text, but keep the labels
            display_text = text
            if "<|ref|>" in text or "<|grounding|>" in text:
                display_text = clean_grounding_text(text)

            # If display text is empty after cleaning but we have boxes, show the labels
            if not display_text and boxes:
                display_text = ", ".join([b["label"] for b in boxes])

            # Emit result
            result = {
                'success': True,
                'text': display_text,
                'raw_text': text,
                'boxes': boxes,
                'image_dims': {'w': orig_w, 'h': orig_h},
                'metadata': {
                    'mode': self.params.get('mode', 'plain_ocr'),
                    'grounding': self.params.get('grounding', False),
                    'base_size': self.params.get('base_size', 1024),
                    'image_size': self.params.get('image_size', 640),
                    'crop_mode': self.params.get('crop_mode', True),
                }
            }

            self.progress_signal.emit("✅ OCR completed successfully!")
            self.result_signal.emit(result)

        except Exception as e:
            error_msg = f"OCR Error: {type(e).__name__}: {str(e)}"
            self.error_signal.emit(error_msg)

        finally:
            # Cleanup temporary directory
            if out_dir and os.path.exists(out_dir):
                shutil.rmtree(out_dir, ignore_errors=True)


class OCRProcessor:
    """Manager for OCR processing with worker thread"""

    def __init__(self, model, tokenizer):
        """Initialize OCR processor

        Args:
            model: DeepSeek-OCR model
            tokenizer: Model tokenizer
        """
        self.model = model
        self.tokenizer = tokenizer
        self.current_worker = None

    def process_image(self, image_path: str, params: dict) -> OCRWorker:
        """Start OCR processing for an image

        Args:
            image_path: Path to image file
            params: Processing parameters

        Returns:
            OCRWorker thread (caller should connect signals and start)
        """
        # Stop previous worker if running
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.quit()
            self.current_worker.wait()

        # Create new worker
        self.current_worker = OCRWorker(
            self.model,
            self.tokenizer,
            image_path,
            params
        )

        return self.current_worker

    def is_processing(self) -> bool:
        """Check if currently processing

        Returns:
            True if worker is running
        """
        return self.current_worker and self.current_worker.isRunning()
