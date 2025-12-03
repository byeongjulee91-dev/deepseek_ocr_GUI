# DeepSeek-OCR Desktop Application

PySide6 기반 DeepSeek-OCR 데스크탑 GUI 애플리케이션

강력한 AI 모델을 활용한 전문적인 OCR 및 PDF 처리 데스크탑 애플리케이션입니다.

## 현재 상태: Phase 6 완료 ✅

**🎉 프로젝트 완성!**

- ✨ 완전한 기능의 데스크탑 애플리케이션
- 📦 PyInstaller로 패키징 가능
- 🚀 프로덕션 배포 준비 완료

**구현된 기능:**

### Phase 1 (완료)
- ✅ 프로젝트 구조 설정
- ✅ 백그라운드 스레드에서 모델 로딩
- ✅ 모델 로딩 진행 다이얼로그
- ✅ 기본 MainWindow (빈 패널)
- ✅ 설정 관리 (QSettings)
- ✅ 유틸리티 함수 (prompt_builder, coordinate_parser)

### Phase 2 (완료)
- ✅ ImageUploadWidget - 드래그앤드롭, 파일 브라우저, 클립보드 붙여넣기
- ✅ OCRProcessor - QThread 기반 비동기 OCR 추론
- ✅ ResultViewerWidget - HTML/Markdown/Plain text 자동 감지 및 렌더링
- ✅ MainWindow 통합 - 모든 위젯 연결 및 시그널 처리
- ✅ Plain OCR 모드 완전 작동

### Phase 3 (완료)
- ✅ ModeSelectorWidget - 4가지 모드 선택 (Plain OCR, Describe, Find, Freeform)
- ✅ BoundingBoxCanvas - QPainter로 바운딩 박스 렌더링
- ✅ 이미지 탭 - 바운딩 박스 오버레이와 함께 이미지 표시
- ✅ 동적 입력 필드 - Find 모드용 검색어, Freeform 모드용 사용자 정의 프롬프트
- ✅ **모든 4가지 OCR 모드 완전 작동!**

### Phase 4 (완료)
- ✅ PDFProcessor - QThread 기반 다중 페이지 PDF 처리
- ✅ PDFProcessorWidget - 포맷 선택, DPI 설정, 이미지 추출 옵션
- ✅ 문서 변환 - Markdown, HTML, DOCX, JSON 출력 지원
- ✅ 페이지별 진행률 표시 - 실시간 진행률 바 및 상태 업데이트
- ✅ 파일 타입 토글 - Image/PDF 전환 기능
- ✅ **PDF 처리 완전 작동!**

### Phase 5 (완료)
- ✅ AdvancedSettingsWidget - 접을 수 있는 고급 설정 패널
- ✅ SettingsDialog - 종합 설정 관리 다이얼로그 (모델, 처리, PDF, UI 설정)
- ✅ 메뉴 바 기능 연결 - Open, Copy, Settings 완전 작동
- ✅ 키보드 단축키 - F5, Escape, Ctrl+T, Ctrl+Shift+S 등 다양한 단축키
- ✅ QSS 스타일링 - 세련된 다크 테마 적용
- ✅ **UI 완성 및 UX 개선!**

### Phase 6 (완료) 🎉
- ✅ PyInstaller spec 파일 - 최적화된 빌드 설정
- ✅ 빌드 스크립트 - Linux/Mac (build.sh), Windows (build.bat)
- ✅ Hidden imports 처리 - PySide6, PyTorch, Transformers 등
- ✅ 리소스 파일 패키징 - QSS 스타일시트 포함
- ✅ 배포 가이드 - DISTRIBUTION.md 문서화
- ✅ **프로덕션 준비 완료!**

## 요구사항

### 하드웨어
- NVIDIA GPU (CUDA 지원)
- 8GB+ VRAM 권장
- 16GB+ 시스템 RAM

### 소프트웨어
- Python 3.8+
- CUDA 11.8+ (NVIDIA 드라이버와 함께)
- pip

## 설치

### 사전 요구사항
- [uv](https://github.com/astral-sh/uv) - 빠른 Python 패키지 관리자
  ```bash
  # uv 설치 (Linux/Mac)
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # uv 설치 (Windows)
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

1. **저장소 클론 및 디렉토리 이동:**
   ```bash
   cd deepseek_ocr_desktop
   ```

2. **가상 환경 생성 및 활성화:**
   ```bash
   # 가상 환경 생성 (uv는 .venv 디렉토리 사용)
   uv venv

   # 가상 환경 활성화
   source .venv/bin/activate  # Linux/Mac
   # 또는
   .venv\Scripts\activate  # Windows
   ```

3. **의존성 설치:**
   ```bash
   uv pip install -r requirements.txt
   ```

## 실행

### 방법 1: uv run 사용 (권장)
```bash
cd deepseek_ocr_desktop
uv run run.py
```

### 방법 2: Python 직접 실행
```bash
cd deepseek_ocr_desktop
python run.py
```

### 방법 3: 가상환경 활성화 후 실행
```bash
cd deepseek_ocr_desktop
source .venv/bin/activate  # Linux/Mac
# 또는
.venv\Scripts\activate  # Windows

python run.py
```

**첫 실행 시:**
- 모델 다운로드: ~5-10GB (시간이 걸릴 수 있음)
- HuggingFace 캐시에 저장: `~/.cache/huggingface/`

## 프로젝트 구조

```
deepseek_ocr_desktop/
├── run.py                      # 애플리케이션 런처 ✅
├── verify_setup.py             # 설정 검증 스크립트 ✅
├── QUICKSTART.md               # 빠른 시작 가이드 ✅
├── MIGRATION_GUIDE.md          # uv 마이그레이션 가이드 ✅
├── CHANGELOG_UV.md             # uv 통합 변경 로그 ✅
├── LOGGING_GUIDE.md            # 로깅 시스템 가이드 ✅
├── src/
│   ├── __init__.py             # Python 패키지 마커 ✅
│   ├── main.py                 # 애플리케이션 진입점 ✅
│   ├── core/                   # 핵심 로직
│   │   ├── __init__.py         # ✅
│   │   ├── model_manager.py    # 모델 로딩 (QThread) ✅
│   │   ├── ocr_processor.py    # OCR 추론 ✅
│   │   ├── pdf_processor.py    # PDF 처리 ✅
│   │   ├── prompt_builder.py   # 프롬프트 생성 ✅
│   │   └── coordinate_parser.py # 바운딩 박스 파싱 ✅
│   ├── ui/                     # UI 컴포넌트
│   │   ├── __init__.py         # ✅
│   │   ├── main_window.py      # 메인 윈도우 ✅
│   │   ├── widgets/            # UI 위젯들
│   │   │   ├── __init__.py     # ✅
│   │   │   ├── image_upload_widget.py    # ✅ Phase 2
│   │   │   ├── mode_selector_widget.py   # ✅ Phase 3
│   │   │   ├── result_viewer_widget.py   # ✅ Phase 3
│   │   │   ├── bounding_box_canvas.py    # ✅ Phase 3
│   │   │   ├── pdf_processor_widget.py   # ✅ Phase 4
│   │   │   └── advanced_settings_widget.py # ✅ Phase 5
│   │   └── dialogs/
│   │       ├── __init__.py     # ✅
│   │       ├── model_loading_dialog.py   # ✅ Phase 1
│   │       └── settings_dialog.py        # ✅ Phase 5
│   ├── utils/                  # 유틸리티
│   │   ├── __init__.py         # ✅
│   │   ├── pdf_utils.py        # PDF 처리 유틸 ✅
│   │   ├── format_converter.py # 문서 변환 ✅
│   │   ├── config.py           # 설정 관리 ✅
│   │   └── logger.py           # 로깅 시스템 ✅
│   └── resources/              # 리소스
│       ├── __init__.py         # ✅
│       ├── icons/
│       └── styles/
│           └── app.qss         # QSS 스타일시트 ✅ Phase 5
├── deepseek_ocr.spec           # PyInstaller 설정 ✅ Phase 6
├── build.sh                    # Linux/Mac 빌드 스크립트 ✅ Phase 6
├── build.bat                   # Windows 빌드 스크립트 ✅ Phase 6
├── requirements.txt            # Python 의존성 ✅
├── DISTRIBUTION.md             # 배포 가이드 ✅ Phase 6
└── README.md                   # 이 파일 ✅
```

## 설정

애플리케이션 설정은 QSettings를 통해 자동으로 저장됩니다:

**Linux:** `~/.config/DeepSeekOCR/DesktopApp.conf`
**Windows:** `HKEY_CURRENT_USER\Software\DeepSeekOCR\DesktopApp`
**macOS:** `~/Library/Preferences/com.DeepSeekOCR.DesktopApp.plist`

### 설정 가능한 옵션

```python
# 모델 설정
model/name = "deepseek-ai/DeepSeek-OCR"
model/hf_home = "~/.cache/huggingface"

# 처리 설정
processing/base_size = 1024
processing/image_size = 640
processing/crop_mode = True

# PDF 설정
pdf/dpi = 144
pdf/extract_images = True
```

## 개발 로드맵

- [x] **Phase 1:** 기본 앱 구조 + 모델 로딩 ✅
- [x] **Phase 2:** 이미지 OCR - Plain OCR 모드 완전 작동 ✅
- [x] **Phase 3:** 모든 OCR 모드 + 바운딩 박스 ✅
- [x] **Phase 4:** PDF 처리 ✅
- [x] **Phase 5:** 고급 설정 & UI 마무리 ✅
- [x] **Phase 6:** PyInstaller 패키징 ✅

**🎉 프로젝트 완성! 모든 Phase 완료!**

## 애플리케이션 사용 방법

### 개발 모드 (소스에서 실행)

```bash
cd /home/byeongjulee/project/deepseek_ocr_GUI/deepseek_ocr_desktop
uv run run.py
```

### 배포 모드 (실행 파일 빌드)

**빌드 방법:**

Linux/Mac:
```bash
cd /home/byeongjulee/project/deepseek_ocr_GUI/deepseek_ocr_desktop
./build.sh
```

Windows:
```cmd
cd deepseek_ocr_desktop
build.bat
```

**실행:**
```bash
# 빌드 후
cd dist/DeepSeek-OCR
./DeepSeek-OCR  # Linux/Mac
DeepSeek-OCR.exe  # Windows
```

자세한 빌드 및 배포 가이드는 [DISTRIBUTION.md](DISTRIBUTION.md) 참조

### 이미지 OCR

**사용 방법:**
1. 애플리케이션이 시작되고 모델이 로드됩니다 (5-30초)
2. 왼쪽 패널 상단에서 **📸 Image** 선택 (기본값)
3. 이미지를 드래그앤드롭하거나 클릭하여 업로드
4. **OCR 모드 선택** (4가지 중 하나):
   - 🔤 **Plain OCR**: 이미지에서 모든 텍스트 추출
   - 👁️ **Describe**: 이미지 설명 생성
   - 🔍 **Find**: 특정 텍스트 검색 및 위치 표시 (바운딩 박스)
   - ✨ **Freeform**: 사용자 정의 프롬프트로 특수 작업
5. 모드별 추가 입력:
   - **Find 모드**: 검색할 텍스트 입력 (예: "Total", "Email")
   - **Freeform 모드**: 사용자 정의 프롬프트 입력
6. "🔍 Analyze Image" 버튼 클릭
7. 결과 확인:
   - **📝 Text 탭**: 추출된 텍스트 (HTML/Markdown/Plain 자동 감지)
   - **🖼️ Image 탭**: 바운딩 박스가 오버레이된 이미지
   - **🐛 Debug 탭**: 원본 모델 출력 및 메타데이터
8. 결과를 클립보드에 복사하거나 텍스트 파일로 다운로드

### PDF 처리 (Phase 4 완료!)

**사용 방법:**
1. 왼쪽 패널 상단에서 **📄 PDF** 선택
2. PDF 파일을 드래그앤드롭하거나 클릭하여 업로드
3. **출력 포맷 선택**:
   - 📝 **Markdown (.md)**: 마크다운 형식
   - 🌐 **HTML (.html)**: 웹 페이지 형식
   - 📄 **Word Document (.docx)**: MS Word 문서
   - 📊 **JSON (.json)**: 구조화된 데이터
4. **PDF 설정 조정** (선택사항):
   - **Resolution (DPI)**: 72-300 DPI (기본값: 144)
   - **Extract embedded images**: 이미지 추출 여부
5. "📄 Process PDF" 버튼 클릭
6. **진행률 확인**:
   - 실시간 진행률 바 (페이지별)
   - 페이지별 처리 상세 정보
7. 처리 완료 후 "💾 Save Document" 버튼으로 저장

### 고급 설정 & 키보드 단축키 (Phase 5 완료!)

**고급 설정:**
- 왼쪽 패널 하단의 "⚙️ Advanced Settings" 클릭하여 펼치기
- Base Size, Image Size, Crop Mode 등 OCR 파라미터 조정
- "💾 Save as Default"로 설정 저장

**종합 설정 (Ctrl+,):**
- Edit → Settings 메뉴 또는 Ctrl+, 단축키
- 모델 설정, 처리 옵션, PDF 설정, UI 설정 등 모든 설정 관리

**키보드 단축키 (F1 눌러서 확인):**
- **F5**: 처리 시작 (Analyze/Process)
- **Escape**: 현재 파일 클리어
- **Ctrl+O**: 파일 열기
- **Ctrl+T**: Image/PDF 모드 전환
- **Ctrl+C**: 결과 복사
- **Ctrl+Shift+S**: 결과 저장
- **Ctrl+,**: 설정 열기
- **F1**: 키보드 단축키 보기
- **Ctrl+Q**: 애플리케이션 종료

**지원 기능:**
- 📸 이미지 업로드: 드래그앤드롭, 파일 브라우저, Ctrl+V 붙여넣기
- 📄 PDF 업로드: 드래그앤드롭, 파일 브라우저
- 🎯 4가지 OCR 모드 (이미지): Plain OCR, Describe, Find, Freeform
- 📦 바운딩 박스 시각화: QPainter로 렌더링된 컬러 박스
- 📋 결과 복사/다운로드
- 🐛 디버그 정보 확인
- 📑 다중 페이지 PDF 처리 (페이지별 진행률)
- 📝 다양한 출력 포맷 (Markdown, HTML, DOCX, JSON)
- ⚙️ 고급 설정: 모든 OCR 파라미터 조정 가능
- ⌨️ 키보드 단축키: 빠른 작업을 위한 다양한 단축키
- 🎨 세련된 UI: 다크 테마 기반 현대적인 디자인

## 로깅 및 디버깅

애플리케이션은 상세한 로깅 시스템을 제공합니다.

### 로그 파일 위치
```bash
# Linux/Mac
~/.deepseek_ocr/logs/deepseek_ocr_YYYYMMDD.log

# Windows
%USERPROFILE%\.deepseek_ocr\logs\deepseek_ocr_YYYYMMDD.log
```

### 로그 보기
```bash
# 실시간 로그 (Linux/Mac)
tail -f ~/.deepseek_ocr/logs/deepseek_ocr_$(date +%Y%m%d).log

# 에러만 보기
grep "ERROR" ~/.deepseek_ocr/logs/deepseek_ocr_*.log
```

### PDF 디버깅
PDF output이 비어있을 때:
1. 로그 파일 확인
2. `OCR complete - text length` 검색
3. `conversion complete` 검색
4. `ERROR` 메시지 확인

자세한 내용은 [LOGGING_GUIDE.md](LOGGING_GUIDE.md) 참조

## 문제 해결

### CUDA를 사용할 수 없음
```
CUDA is not available. This application requires an NVIDIA GPU with CUDA support.
```

**해결책:**
1. NVIDIA 드라이버가 설치되었는지 확인: `nvidia-smi`
2. CUDA Toolkit 설치 확인
3. PyTorch CUDA 버전 확인: `python -c "import torch; print(torch.cuda.is_available())"`

### 모델 로딩 실패
- 인터넷 연결 확인 (첫 실행 시 다운로드 필요)
- 디스크 공간 확인 (~10GB 필요)
- HuggingFace 캐시 디렉토리 권한 확인

### Out of Memory (OOM)
- GPU VRAM이 부족합니다
- 최소 8GB VRAM 필요
- 다른 GPU 프로그램 종료

## 라이선스

이 프로젝트는 원본 DeepSeek-OCR 웹 애플리케이션에서 리팩토링되었습니다.

## 기여

Phase 1이 완료되었습니다. Phase 2부터 기여를 환영합니다!
