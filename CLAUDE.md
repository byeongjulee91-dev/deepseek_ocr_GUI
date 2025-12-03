# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains **two complete OCR applications** powered by DeepSeek-OCR:

1. **Web Application** (root directory) - React + FastAPI + Docker
2. **Desktop Application** (`deepseek_ocr_desktop/`) - PySide6 standalone GUI

Both applications share core OCR functionality but use different UI frameworks and deployment methods.

---

## Web Application (React + FastAPI)

### Development Commands

#### Docker Workflow (Primary Development Method)

```bash
# Start the application (first run downloads ~5-10GB model)
docker compose up --build

# Restart after code changes
docker compose down
docker compose up --build

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Rebuild single service
docker compose up --build backend
docker compose up --build frontend
```

#### Frontend Development (without Docker)

```bash
cd frontend

# Install dependencies
npm install

# Development server with hot reload
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

#### Backend Development (without Docker)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run server (requires GPU)
python main.py
```

#### Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key environment variables:
- `API_PORT`: Backend API port (default: 8000)
- `FRONTEND_PORT`: Frontend port (default: 3000)
- `MAX_UPLOAD_SIZE_MB`: File upload limit (default: 100)
- `BASE_SIZE`: OCR processing resolution (default: 1024)
- `IMAGE_SIZE`: Tile size for large images (default: 640)
- `MODEL_NAME`: HuggingFace model identifier (default: deepseek-ai/DeepSeek-OCR)
- `HF_HOME`: Model cache directory (default: /models)

### Architecture Overview

**Stack**: React 18 + Vite 5 → Nginx → FastAPI + PyTorch + DeepSeek-OCR

The application is containerized with Docker Compose:
- **Frontend container**: Multi-stage build (Node.js build → Nginx serve)
- **Backend container**: Python + PyTorch with GPU access (nvidia-docker)
- **Shared volume**: Model cache (`./models:/models`)

#### Backend (FastAPI)

**Entry Point**: `backend/main.py`

The backend uses FastAPI lifespan events to load the DeepSeek-OCR model on startup. The model is loaded once into GPU memory and shared across all requests.

**Two Main Endpoints:**

1. **`POST /api/ocr`**: Single image OCR processing
   - Handles 4 core modes: `plain_ocr`, `describe`, `find_ref`, `freeform`
   - Returns extracted text and optional bounding boxes
   - Coordinate system: Model outputs 0-999 normalized coords, backend scales to actual pixels

2. **`POST /api/process-pdf`**: Multi-page PDF processing
   - Converts PDF pages to images (using PyMuPDF/fitz)
   - Processes each page through OCR pipeline
   - Converts results to markdown, HTML, DOCX, or JSON
   - Supports automatic image extraction from PDFs

**Key Modules**:
- `pdf_utils.py`: PDF→image conversion, coordinate parsing, image extraction from reference tags
- `format_converter.py`: Document conversion to MD/HTML/DOCX with formatting preservation

**Important Implementation Details**:
- Model loads in bfloat16 precision on CUDA
- Uses normalized coordinate system (0-999) that **must** be scaled to image dimensions before returning
- Supports multiple bounding boxes for terms that appear multiple times
- Grounding tags format: `<|ref|>label<|/ref|><|det|>[[x1,y1,x2,y2]]<|/det|>`
- Tags must be cleaned from output using `clean_grounding_text()` before display

#### Frontend (React + Vite)

**Entry Point**: `frontend/src/App.jsx`

Dual-mode interface with toggle between Image OCR and PDF Processing.

**Key Components**:
- `ImageUpload.jsx`: Drag-and-drop file upload for images and PDFs
- `PDFProcessor.jsx`: PDF-specific UI with format selection and progress tracking
- `ModeSelector.jsx`: Selects OCR mode (plain_ocr, describe, find_ref, freeform)
- `ResultPanel.jsx`: Displays results with HTML/Markdown rendering and bounding box overlay
- `AdvancedSettings.jsx`: Exposes processing parameters (base_size, image_size, crop_mode)

**Styling**: TailwindCSS with custom glass morphism design + Framer Motion animations

**State Management**: React hooks (useState, useEffect) - no external state library

### Critical Implementation Details

#### Coordinate System & Bounding Boxes

The DeepSeek-OCR model outputs **normalized coordinates** (0-999 range) that must be scaled to actual image dimensions:

```python
# Backend scaling (main.py:231-234)
x1 = int(float(box[0]) / 999 * image_width)
y1 = int(float(box[1]) / 999 * image_height)
x2 = int(float(box[2]) / 999 * image_width)
y2 = int(float(box[3]) / 999 * image_height)
```

**Multiple Bounding Boxes**: The model can return multiple boxes for repeated terms:
```
<|ref|>label<|/ref|><|det|>[[x1,y1,x2,y2], [x1,y1,x2,y2], ...]<|/det|>
```

The parser in `main.py:parse_detections()` handles both single boxes `[x1,y1,x2,y2]` and multiple boxes `[[x1,y1,x2,y2], ...]` using `ast.literal_eval()`.

**CRITICAL**: Always scale coordinates from 0-999 to actual pixels before returning to frontend. Forgetting this will result in incorrect bounding box positions.

#### PDF Processing Pipeline

1. **Convert PDF to images** (`pdf_utils.py:pdf_to_images_high_quality`): PyMuPDF with configurable DPI
2. **Process each page** through OCR inference (same as single image)
3. **Extract images** if requested (detects `<|ref|>image<|/ref|>` tags and crops regions)
4. **Clean output** by removing reference tags with `clean_markdown_content()`
5. **Convert to format** using `DocumentConverter` class:
   - **Markdown**: Text with embedded base64 images
   - **HTML**: Styled document with CSS, embedded images, table formatting
   - **DOCX**: Uses python-docx to create Word documents with formatting preservation
   - **JSON**: Structured data with per-page text, boxes, and metadata

#### Dynamic Image Cropping

For images larger than 640x640 pixels, the model uses dynamic cropping:
- Images are split into tiles based on aspect ratio
- Global view (BASE_SIZE) + local views (IMAGE_SIZE tiles)
- Controlled by `crop_mode` parameter (default: true)
- Implemented in the model's `infer()` method

### OCR Modes

- **plain_ocr**: Basic text extraction (most reliable, fastest)
- **describe**: Image description (for visual understanding)
- **find_ref**: Locate specific terms with bounding boxes (grounding auto-enabled)
- **freeform**: Custom prompts (advanced use cases)

**Note**: The application originally had 12 modes but was simplified to 4 core working modes in v2.1.1. Additional modes (tables_csv, tables_md, kv_json, figure_chart, layout_map, pii_redact, multilingual) exist in code (`main.py:build_prompt()`) but are not exposed in UI.

### Common Issues & Gotchas

#### Coordinate Scaling
**Most common bug**: Forgetting to scale model outputs from 0-999 to actual pixels. Always use the formula: `actual_coord = (normalized_coord / 999) * image_dimension`

#### Image Upload Size
Upload limits configured via:
- Nginx `client_max_body_size` in `frontend/nginx.conf` (set to 100M)
- FastAPI (no explicit limit, uses nginx)
- Environment variable `MAX_UPLOAD_SIZE_MB` in `.env`

#### Grounding Tag Cleanup
Raw model output contains tags like `<|ref|>`, `<|det|>`, `<|grounding|>`. Backend must clean these before returning to frontend using `clean_grounding_text()`. Frontend should never see raw tags.

#### PDF Format Conversion Performance
- JSON format is fastest (no conversion overhead)
- DOCX takes longest due to formatting and image processing
- HTML/Markdown are intermediate in processing time

#### HTML vs Markdown Output
The model outputs HTML (especially for tables), not Markdown. Frontend detects and renders HTML properly using `dangerouslySetInnerHTML`.

### File Structure

```
deepseek_ocr_GUI/
├── backend/
│   ├── main.py              # FastAPI app, model loading, endpoints
│   ├── pdf_utils.py         # PDF processing utilities
│   ├── format_converter.py  # Document format conversion
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Backend container
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.jsx          # Main app with dual mode
│   │   └── main.jsx         # React entry point
│   ├── nginx.conf           # Nginx reverse proxy config
│   ├── package.json         # Node dependencies
│   └── Dockerfile           # Frontend container (multi-stage build)
├── models/                  # Model cache (Docker volume)
├── .env                     # Environment configuration
├── .env.example             # Environment template
├── docker-compose.yml       # Container orchestration
└── deepseek_ocr_desktop/    # Desktop application (separate project)
```

### GPU Requirements

#### NVIDIA Driver Installation (Blackwell/RTX 5090)
For RTX 5090 on Ubuntu 24.04:
1. Use open-source driver (nvidia-driver-580-open or newer)
2. Upgrade to kernel 6.11+ (6.14+ recommended)
3. **Enable Resize Bar in BIOS/UEFI** (critical!)

#### NVIDIA Container Toolkit
Required for GPU access in Docker. Installation: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

Verify GPU access:
```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

---

## Desktop Application (PySide6)

Located in `deepseek_ocr_desktop/` directory.

### Development Commands

#### Running from Source

```bash
cd deepseek_ocr_desktop

# Install uv if not already installed
# Linux/Mac: curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Create virtual environment (first time)
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
uv pip install -r requirements.txt

# Run application
uv run run.py
# or
python run.py
```

#### Building Standalone Executable

```bash
cd deepseek_ocr_desktop

# Linux/Mac
./build.sh

# Windows
build.bat

# Run built executable
cd dist/DeepSeek-OCR
./DeepSeek-OCR  # Linux/Mac
DeepSeek-OCR.exe  # Windows
```

### Architecture Overview

**Stack**: PySide6 (Qt for Python) + PyTorch + DeepSeek-OCR

The desktop application is a standalone GUI that loads the model directly (no client-server architecture like the web app).

**Key Architectural Differences from Web App**:
- No HTTP API - direct model loading in the same process
- QThread-based async processing instead of FastAPI async
- QSettings for configuration instead of .env files
- QPainter for bounding box rendering instead of HTML canvas

#### Project Structure

```
deepseek_ocr_desktop/
├── src/
│   ├── main.py                 # Application entry point
│   ├── core/                   # Core logic (shared concepts with backend/)
│   │   ├── model_manager.py    # Model loading (QThread-based)
│   │   ├── ocr_processor.py    # OCR inference (QThread worker)
│   │   ├── pdf_processor.py    # PDF processing (QThread worker)
│   │   ├── prompt_builder.py   # Prompt generation (same as web backend)
│   │   └── coordinate_parser.py # Bounding box parsing (same as web backend)
│   ├── ui/                     # UI components
│   │   ├── main_window.py      # Main window
│   │   ├── widgets/            # UI widgets
│   │   │   ├── image_upload_widget.py
│   │   │   ├── mode_selector_widget.py
│   │   │   ├── result_viewer_widget.py
│   │   │   ├── bounding_box_canvas.py  # QPainter rendering
│   │   │   ├── pdf_processor_widget.py
│   │   │   └── advanced_settings_widget.py
│   │   └── dialogs/
│   │       ├── model_loading_dialog.py
│   │       └── settings_dialog.py
│   └── utils/                  # Utilities (same as web backend)
│       ├── pdf_utils.py        # PDF processing
│       ├── format_converter.py # Document conversion
│       └── config.py           # QSettings wrapper
├── deepseek_ocr.spec           # PyInstaller configuration
├── build.sh / build.bat        # Build scripts
└── requirements.txt            # Python dependencies
```

#### Code Sharing Between Web & Desktop

The following modules are **shared/duplicated** between web and desktop apps:
- `pdf_utils.py`: PDF processing utilities
- `format_converter.py`: Document conversion to MD/HTML/DOCX
- `prompt_builder.py`: Prompt construction logic
- `coordinate_parser.py`: Bounding box parsing

**Important**: When fixing bugs in these modules, check if the fix needs to be applied to both `backend/` and `deepseek_ocr_desktop/src/utils/`.

#### Desktop-Specific Features

**QThread Architecture**:
- `ModelManager` (QThread): Loads model in background, emits progress signals
- `OCRProcessor` (QThread): Runs OCR inference without blocking UI
- `PDFProcessor` (QThread): Processes PDF pages with progress updates

**Settings Management**:
- Uses QSettings (platform-specific storage)
- Linux: `~/.config/DeepSeekOCR/DesktopApp.conf`
- Windows: `HKEY_CURRENT_USER\Software\DeepSeekOCR\DesktopApp`
- macOS: `~/Library/Preferences/com.DeepSeekOCR.DesktopApp.plist`

**Keyboard Shortcuts**:
- F5: Process/Analyze
- Escape: Clear file
- Ctrl+O: Open file
- Ctrl+T: Toggle Image/PDF mode
- Ctrl+C: Copy result
- Ctrl+Shift+S: Save result
- Ctrl+,: Settings dialog
- F1: Show shortcuts
- Ctrl+Q: Quit

**Clipboard Paste**: Desktop app supports Ctrl+V to paste images from clipboard (unique to desktop).

### Building & Distribution

The desktop app uses PyInstaller for creating standalone executables. Key considerations:

**Hidden Imports** (in `deepseek_ocr.spec`):
- PySide6 modules (QtCore, QtGui, QtWidgets, etc.)
- PyTorch and Transformers modules
- PIL/Pillow modules

**Data Files**:
- QSS stylesheets from `src/resources/styles/`
- Icons from `src/resources/icons/` (if any)

**Build Issues**:
- Ensure all hidden imports are declared
- Model files are NOT bundled (too large) - downloaded on first run
- CUDA/cuDNN libraries may need manual inclusion on Windows

See `DISTRIBUTION.md` in `deepseek_ocr_desktop/` for detailed build instructions.

---

## Common Workflows

### Adding a New OCR Mode

1. **Backend**: Update `build_prompt()` in `backend/main.py` (web) and `deepseek_ocr_desktop/src/core/prompt_builder.py` (desktop)
2. **Frontend (web)**: Add mode to `ModeSelector.jsx`
3. **Frontend (desktop)**: Add mode to `mode_selector_widget.py`
4. Test with sample images to ensure prompt works correctly

### Fixing Coordinate Scaling Bugs

1. Check `backend/main.py:parse_detections()` (web)
2. Check `deepseek_ocr_desktop/src/core/coordinate_parser.py` (desktop)
3. Ensure scaling formula: `actual = (normalized / 999) * dimension`
4. Test with `find_ref` mode to verify bounding boxes

### Adding PDF Features

1. **Shared**: Update `pdf_utils.py` and `format_converter.py` in both projects
2. **Web**: Update `/api/process-pdf` endpoint in `backend/main.py`
3. **Desktop**: Update `PDFProcessor` QThread in `deepseek_ocr_desktop/src/core/pdf_processor.py`
4. Test with multi-page PDFs, verify all output formats

### Updating Dependencies

**Web App**:
```bash
# Backend
cd backend
pip freeze > requirements.txt

# Frontend
cd frontend
npm update
```

**Desktop App**:
```bash
cd deepseek_ocr_desktop
pip freeze > requirements.txt
# Rebuild to test
./build.sh  # or build.bat
```

---

## Testing

### Manual Testing Checklist

**Image OCR** (both web & desktop):
- [ ] Upload image via drag-and-drop
- [ ] Upload image via file browser
- [ ] (Desktop only) Paste image via Ctrl+V
- [ ] Test all 4 modes: plain_ocr, describe, find_ref, freeform
- [ ] Verify bounding boxes display correctly (find_ref mode)
- [ ] Test with large images (>640x640) to verify dynamic cropping
- [ ] Copy result to clipboard
- [ ] Download result as text file

**PDF Processing** (both web & desktop):
- [ ] Upload PDF via drag-and-drop
- [ ] Upload PDF via file browser
- [ ] Test all output formats: markdown, html, docx, json
- [ ] Verify multi-page progress tracking
- [ ] Test image extraction option
- [ ] Test different DPI settings (72, 144, 300)
- [ ] Download converted document

**Advanced Settings**:
- [ ] Modify base_size, image_size, crop_mode
- [ ] Verify settings persist across restarts
- [ ] Test edge cases (base_size < image_size)

### Known Constraints

- **GPU Required**: Both applications require CUDA-capable NVIDIA GPU
- **Model Size**: ~5-10GB (downloads on first run, cached)
- **VRAM**: Minimum 8-12GB VRAM recommended
- **Processing Time**: Increases with PDF page count and DPI
- **Upload Limits**: 100MB default (configurable via .env for web)

---

## Troubleshooting

### Model Loading Issues

**Symptom**: Model fails to load, OOM errors
**Solutions**:
- Check GPU availability: `nvidia-smi`
- Verify CUDA: `python -c "import torch; print(torch.cuda.is_available())"`
- Ensure sufficient VRAM (8GB minimum)
- Check disk space for model cache (~10GB)
- Clear HuggingFace cache if corrupted: `rm -rf ~/.cache/huggingface/`

### Bounding Boxes Not Showing

**Symptom**: No bounding boxes displayed in find_ref mode
**Solutions**:
- Verify grounding is enabled for find_ref mode
- Check coordinate scaling in `parse_detections()` function
- Inspect raw model output in debug tab (web) or console (desktop)
- Ensure find_term is not empty

### PDF Processing Fails

**Symptom**: PDF upload fails or produces empty output
**Solutions**:
- Check PDF is not encrypted or password-protected
- Verify PyMuPDF (fitz) is installed correctly
- Test with simple PDF (single page, no complex formatting)
- Check DPI setting (144 default, max 300)
- Verify disk space for temporary image files

### Desktop App Won't Start

**Symptom**: Desktop executable crashes on startup
**Solutions**:
- Run from terminal to see error messages
- Check CUDA availability (desktop requires GPU even for UI)
- Verify all dependencies in requirements.txt are installed
- On Windows, ensure CUDA/cuDNN DLLs are in PATH
- Try running from source (`python main.py`) to isolate PyInstaller issues

---

## Additional Resources

- **DeepSeek-OCR Model**: https://huggingface.co/deepseek-ai/DeepSeek-OCR
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **PySide6 Documentation**: https://doc.qt.io/qtforpython-6/
- **PyInstaller Guide**: https://pyinstaller.org/en/stable/
- **NVIDIA Container Toolkit**: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/
