# DeepSeek-OCR Desktop - Quick Start Guide

## 빠른 시작

### 1. 의존성 설치

#### uv 설치 (처음 한 번만)
```bash
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 프로젝트 의존성 설치
```bash
cd deepseek_ocr_desktop

# 가상 환경 생성
uv venv

# 가상 환경 활성화
source .venv/bin/activate  # Linux/Mac
# 또는
.venv\Scripts\activate  # Windows

# 의존성 설치
uv pip install -r requirements.txt

# (선택사항) 설정 검증
python verify_setup.py
```

### 2. 애플리케이션 실행

**⚠️ 중요: 반드시 프로젝트 루트 디렉토리에서 실행하세요!**

#### 방법 1: uv run 사용 (가장 간단, 의존성 자동 설치)
```bash
cd deepseek_ocr_desktop
uv run run.py
```

#### 방법 2: 가상환경 활성화 후 실행
```bash
cd deepseek_ocr_desktop
source .venv/bin/activate  # Linux/Mac
# 또는
.venv\Scripts\activate  # Windows

python run.py
```

#### ❌ 잘못된 실행 방법
```bash
# 이렇게 하면 ImportError 발생!
cd src
python main.py  # ❌ 동작하지 않음!
```

### 3. 첫 실행 시

- **모델 다운로드**: 약 5-10GB (HuggingFace에서 자동 다운로드)
- **다운로드 위치**: `~/.cache/huggingface/` (Linux/Mac) 또는 `%USERPROFILE%\.cache\huggingface\` (Windows)
- **소요 시간**: 인터넷 속도에 따라 5-30분

### 4. 문제 해결

#### ImportError: attempted relative import beyond top-level package
✅ **해결됨!** `__init__.py` 파일과 `run.py` 런처로 해결

#### ModuleNotFoundError: No module named 'PySide6'
```bash
# 가상환경 활성화 후
uv pip install -r requirements.txt
```

#### CUDA not available
- NVIDIA 드라이버 설치 확인: `nvidia-smi`
- PyTorch CUDA 버전 확인: `python -c "import torch; print(torch.cuda.is_available())"`

## 프로젝트 구조 변경 사항

### 추가된 파일

1. **`run.py`** - 애플리케이션 런처
   - `src/` 디렉토리를 Python path에 추가
   - 상대 임포트 문제 해결

2. **`__init__.py` 파일들** - Python 패키지 마커
   - `src/__init__.py`
   - `src/core/__init__.py`
   - `src/ui/__init__.py`
   - `src/ui/widgets/__init__.py`
   - `src/ui/dialogs/__init__.py`
   - `src/utils/__init__.py`
   - `src/resources/__init__.py`

### 실행 방법 변경

**이전:**
```bash
cd src
python main.py  # ❌ ImportError 발생
```

**현재:**
```bash
cd deepseek_ocr_desktop
uv run run.py  # ✅ 정상 작동
# 또는
python run.py
```

## uv 장점

- **속도**: pip보다 10-100배 빠른 패키지 설치
- **효율성**: Rust로 작성되어 매우 효율적
- **호환성**: 기존 `requirements.txt` 파일과 완벽 호환
- **의존성 해결**: 더 빠르고 안정적인 의존성 해결

## 다음 단계

- [README.md](README.md) - 전체 기능 및 사용 방법
- [DISTRIBUTION.md](DISTRIBUTION.md) - 빌드 및 배포 가이드
- [../CLAUDE.md](../CLAUDE.md) - 개발자 가이드
