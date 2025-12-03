"""
PDF Processor
QThread-based worker for processing multi-page PDF documents
Supports both local transformer model and remote vLLM endpoint
Adapted from backend/main.py /api/process-pdf endpoint
"""

import json
import os
import tempfile
import shutil
from typing import Dict, Any, Optional
from PySide6.QtCore import QThread, Signal
from PIL import Image
import io

# Import utilities
from ..utils.pdf_utils import (
    pdf_to_images_high_quality,
    extract_ref_patterns,
    crop_images_from_refs,
    clean_markdown_content
)
from ..utils.format_converter import DocumentConverter
from .prompt_builder import build_prompt
from .coordinate_parser import parse_detections, clean_grounding_text
from .vllm_client import VLLMClient
from ..utils.logger import get_logger, log_pdf_page

# Initialize logger
logger = get_logger(__name__)


class PDFWorker(QThread):
    """Worker thread for processing PDF documents"""

    page_progress_signal = Signal(int, int)  # (current_page, total_pages)
    page_complete_signal = Signal(int, dict)  # (page_num, page_result)
    finished_signal = Signal(dict)  # Final result with converted document
    error_signal = Signal(str)  # Error message
    status_signal = Signal(str)  # Status updates

    def __init__(self, model, tokenizer, pdf_path: str, params: Dict[str, Any]):
        """Initialize PDF worker

        Args:
            model: DeepSeek OCR model or VLLMClient
            tokenizer: Model tokenizer (None for vLLM mode)
            pdf_path: Path to PDF file
            params: Processing parameters
        """
        super().__init__()
        self.model = model
        self.tokenizer = tokenizer
        self.pdf_path = pdf_path
        self.params = params
        self.is_cancelled = False
        self.is_vllm = isinstance(model, VLLMClient)

        logger.info(f"PDFWorker initialized for: {pdf_path}")
        logger.debug(f"Mode: {'vLLM' if self.is_vllm else 'Local'}")
        logger.debug(f"Parameters: {params}")

    def cancel(self):
        """Cancel the processing"""
        self.is_cancelled = True

    def run(self):
        """Process PDF document"""
        try:
            logger.info("="*60)
            logger.info("Starting PDF processing")
            logger.info("="*60)

            # Extract parameters
            output_format = self.params.get('output_format', 'markdown')
            dpi = self.params.get('dpi', 144)
            extract_images = self.params.get('extract_images', True)
            include_caption = self.params.get('include_caption', False)
            base_size = self.params.get('base_size', 1024)
            image_size = self.params.get('image_size', 640)
            crop_mode = self.params.get('crop_mode', True)
            test_compress = self.params.get('test_compress', False)

            logger.info(f"Output format: {output_format}, DPI: {dpi}, Extract images: {extract_images}")
            logger.debug(f"OCR params: base_size={base_size}, image_size={image_size}, crop_mode={crop_mode}")

            # Read PDF file
            self.status_signal.emit("📖 Reading PDF file...")
            logger.info(f"Reading PDF file: {self.pdf_path}")
            with open(self.pdf_path, 'rb') as f:
                pdf_bytes = f.read()
            logger.debug(f"PDF file size: {len(pdf_bytes)} bytes")

            # Convert PDF to images
            self.status_signal.emit(f"🔄 Converting PDF to images at {dpi} DPI...")
            logger.info(f"Converting PDF to images at {dpi} DPI...")
            images = pdf_to_images_high_quality(pdf_bytes, dpi=dpi)
            total_pages = len(images)
            logger.info(f"PDF converted to {total_pages} images")

            if total_pages == 0:
                logger.error("PDF contains no pages")
                self.error_signal.emit("PDF contains no pages")
                return

            self.status_signal.emit(f"📄 Processing {total_pages} pages...")

            # Process each page
            pages_content = []
            all_extracted_images = []

            for page_idx, img in enumerate(images):
                if self.is_cancelled:
                    logger.warning("Processing cancelled by user")
                    self.error_signal.emit("Processing cancelled by user")
                    return

                # Update progress
                page_num = page_idx + 1
                log_pdf_page(logger, page_num, total_pages, "starting")
                self.page_progress_signal.emit(page_num, total_pages)
                self.status_signal.emit(f"🔍 Processing page {page_num}/{total_pages}...")

                # Process page
                page_result = self._process_page(
                    img, page_num,
                    include_caption=include_caption,
                    extract_images=extract_images,
                    base_size=base_size,
                    image_size=image_size,
                    crop_mode=crop_mode,
                    test_compress=test_compress
                )

                if page_result is None:
                    logger.warning(f"Page {page_num} processing failed, skipping")
                    continue  # Skip failed pages

                logger.info(f"Page {page_num} processed successfully - text length: {len(page_result.get('text', ''))}")
                pages_content.append(page_result)

                # Collect extracted images
                if 'extracted_images' in page_result:
                    img_count = len(page_result['extracted_images'])
                    logger.debug(f"Page {page_num}: extracted {img_count} images")
                    all_extracted_images.extend(page_result['extracted_images'])

                # Emit page completion
                self.page_complete_signal.emit(page_num, page_result)
                log_pdf_page(logger, page_num, total_pages, "completed")

            if self.is_cancelled:
                self.error_signal.emit("Processing cancelled by user")
                return

            # Convert to requested format
            self.status_signal.emit(f"📝 Converting to {output_format}...")
            logger.info(f"Converting {len(pages_content)} pages to {output_format} format...")
            converter = DocumentConverter()

            if output_format == 'markdown':
                logger.debug("Converting to Markdown...")
                content = converter.to_markdown(pages_content, include_images=False)
                content_type = 'text/markdown'
                logger.info(f"Markdown conversion complete - {len(content)} characters")
            elif output_format == 'html':
                logger.debug("Converting to HTML...")
                content = converter.to_html(pages_content, include_images=False)
                content_type = 'text/html'
                logger.info(f"HTML conversion complete - {len(content)} characters")
            elif output_format == 'docx':
                logger.debug("Converting to DOCX...")
                docx_buffer = converter.to_docx(pages_content, include_images=False)
                content = docx_buffer.getvalue()
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                logger.info(f"DOCX conversion complete - {len(content)} bytes")
            elif output_format == 'json':
                logger.debug("Converting to JSON...")
                content = json.dumps({
                    'pages': pages_content,
                    'total_pages': total_pages,
                    'extracted_images_count': len(all_extracted_images)
                }, indent=2, ensure_ascii=False)
                content_type = 'application/json'
                logger.info(f"JSON conversion complete - {len(content)} characters")
            else:
                logger.error(f"Unsupported output format: {output_format}")
                self.error_signal.emit(f"Unsupported format: {output_format}")
                return

            # Emit final result
            result = {
                'content': content,
                'content_type': content_type,
                'format': output_format,
                'total_pages': total_pages,
                'pages_content': pages_content,
                'extracted_images': all_extracted_images,
                'extracted_images_count': len(all_extracted_images)
            }

            logger.info("="*60)
            logger.info(f"PDF processing complete!")
            logger.info(f"  Total pages: {total_pages}")
            logger.info(f"  Output format: {output_format}")
            logger.info(f"  Content size: {len(content) if isinstance(content, (str, bytes)) else 'N/A'}")
            logger.info(f"  Extracted images: {len(all_extracted_images)}")
            logger.info("="*60)

            self.status_signal.emit(f"✅ Processing complete! {total_pages} pages processed.")
            self.finished_signal.emit(result)

        except Exception as e:
            import traceback
            error_msg = f"PDF processing error: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            self.error_signal.emit(error_msg)

    def _process_page(self, img: Image.Image, page_num: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Process a single PDF page

        Args:
            img: PIL Image of the page
            page_num: Page number (1-indexed)
            **kwargs: Processing parameters

        Returns:
            Dictionary with page results, or None on error
        """
        out_dir = None
        temp_img_path = None

        try:
            logger.debug(f"Processing page {page_num}...")

            # Save image to temporary BytesIO
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)

            # Get image dimensions
            img_width, img_height = img.size
            logger.debug(f"Page {page_num} dimensions: {img_width}x{img_height}")

            # Build prompt for plain OCR (PDF processing always uses plain OCR)
            prompt = build_prompt(
                mode='plain_ocr',
                user_prompt='',
                grounding=False,
                find_term=None,
                schema=None,
                include_caption=kwargs.get('include_caption', False)
            )
            logger.debug(f"Page {page_num} prompt built (length: {len(prompt)})")

            # Create temporary output directory for model inference
            out_dir = tempfile.mkdtemp(prefix=f"dsocr_pdf_page{page_num}_")
            logger.debug(f"Page {page_num} output directory: {out_dir}")

            # Save temp image for model inference
            temp_img_path = f"/tmp/pdf_page_{page_num}.png"
            img.save(temp_img_path)
            logger.debug(f"Page {page_num} saved to: {temp_img_path}")

            # Perform OCR inference
            logger.info(f"Page {page_num}: Running OCR inference...")
            if self.is_vllm:
                # vLLM mode: Call remote API
                logger.debug(f"Page {page_num}: Using vLLM remote inference")
                result_text = self.model.infer(
                    prompt=prompt,
                    image_file=temp_img_path,
                    base_size=kwargs.get('base_size', 1024),
                    image_size=kwargs.get('image_size', 640),
                    crop_mode=kwargs.get('crop_mode', True),
                )
            else:
                # Local mode: Use transformer model
                logger.debug(f"Page {page_num}: Using local transformer model")
                result_text = self.model.infer(
                    self.tokenizer,
                    prompt=prompt,
                    image_file=temp_img_path,
                    output_path=out_dir,
                    base_size=kwargs.get('base_size', 1024),
                    image_size=kwargs.get('image_size', 640),
                    crop_mode=kwargs.get('crop_mode', True),
                    save_results=False,
                    test_compress=kwargs.get('test_compress', False),
                    eval_mode=True
                )
            logger.info(f"Page {page_num}: OCR complete - text length: {len(result_text) if isinstance(result_text, str) else 'N/A'}")

            # Normalize response (same as ocr_processor.py)
            if isinstance(result_text, str):
                result_text = result_text.strip()
            elif isinstance(result_text, dict) and "text" in result_text:
                result_text = str(result_text["text"]).strip()
            elif isinstance(result_text, (list, tuple)):
                result_text = "\n".join(map(str, result_text)).strip()
            else:
                result_text = ""

            # Fallback: check output file
            if not result_text:
                mmd = os.path.join(out_dir, "result.mmd")
                if os.path.exists(mmd):
                    with open(mmd, "r", encoding="utf-8") as fh:
                        result_text = fh.read().strip()
            if not result_text:
                result_text = "No text returned by model."

            logger.debug(f"Page {page_num} raw text preview: {result_text[:200]}...")

            # Parse bounding boxes (if any)
            boxes = parse_detections(result_text, img_width, img_height)
            logger.debug(f"Page {page_num}: Parsed {len(boxes)} bounding boxes")

            # Clean grounding tags from text
            display_text = clean_grounding_text(result_text)
            logger.debug(f"Page {page_num}: Text cleaned - length: {len(display_text)}")

            # Extract images if requested
            extracted_images = []
            if kwargs.get('extract_images', True):
                logger.debug(f"Page {page_num}: Extracting images from refs...")
                matches, image_refs, other_refs = extract_ref_patterns(result_text)
                logger.debug(f"Page {page_num}: Found {len(image_refs)} image refs, {len(other_refs)} other refs")

                if image_refs:
                    cropped = crop_images_from_refs(img, matches)
                    extracted_images = cropped
                    logger.info(f"Page {page_num}: Extracted {len(extracted_images)} images")

                    # Clean markdown content
                    display_text = clean_markdown_content(display_text, image_refs, other_refs)
                    logger.debug(f"Page {page_num}: Markdown content cleaned")

            result = {
                'page_num': page_num,
                'text': display_text,
                'raw_text': result_text,
                'boxes': boxes,
                'extracted_images': extracted_images,
                'image_dims': {'w': img_width, 'h': img_height}
            }

            logger.debug(f"Page {page_num}: Processing complete")
            return result

        except Exception as e:
            import traceback
            error_msg = f"Error processing page {page_num}: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            # Don't emit error for individual pages, just skip
            return None

        finally:
            # Cleanup temporary directory and image
            if out_dir and os.path.exists(out_dir):
                shutil.rmtree(out_dir, ignore_errors=True)
            if temp_img_path and os.path.exists(temp_img_path):
                try:
                    os.remove(temp_img_path)
                except:
                    pass


class PDFProcessor:
    """Manages PDF processing workers"""

    def __init__(self, model, tokenizer):
        """Initialize PDF processor

        Args:
            model: DeepSeek OCR model or VLLMClient
            tokenizer: Model tokenizer (None for vLLM mode)
        """
        self.model = model
        self.tokenizer = tokenizer
        self.current_worker = None

    def process_pdf(self, pdf_path: str, params: Dict[str, Any]) -> PDFWorker:
        """Start PDF processing

        Args:
            pdf_path: Path to PDF file
            params: Processing parameters

        Returns:
            PDFWorker instance (not started yet, caller should connect signals and start)
        """
        # Create worker
        worker = PDFWorker(self.model, self.tokenizer, pdf_path, params)
        self.current_worker = worker
        return worker

    def cancel_current(self):
        """Cancel current processing"""
        if self.current_worker:
            self.current_worker.cancel()
