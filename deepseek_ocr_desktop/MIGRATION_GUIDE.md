# Migration Guide: uv + Package Structure Fix

## 변경 사항 요약

이 문서는 DeepSeek-OCR Desktop 애플리케이션의 Python 가상환경 관리를 `uv`로 전환하고, ImportError 문제를 해결한 내용을 설명합니다.

## 주요 변경사항

### 1. ✅ uv 도입

**이전 (pip + venv):**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**현재 (uv):**
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

**장점:**
- 10-100배 빠른 패키지 설치
- Rust 기반 고성능
- 기존 requirements.txt와 완벽 호환

### 2. ✅ Python 패키지 구조 수정

**문제:**
```
ImportError: attempted relative import beyond top-level package
```

**원인:**
- `src/` 디렉토리가 Python 패키지로 인식되지 않음
- 상대 임포트 (`from ..core import ...`) 사용 시 오류 발생

**해결:**
1. 모든 디렉토리에 `__init__.py` 추가
2. `run.py` 런처 생성
3. `main.py`의 임포트를 상대 임포트로 변경

### 3. ✅ 실행 방법 변경

**이전 (❌ 동작하지 않음):**
```bash
cd src
python main.py  # ImportError!
```

**현재 (✅ 정상 작동):**
```bash
cd deepseek_ocr_desktop
uv run run.py
# 또는
python run.py
```

## 추가된 파일

### 1. `run.py` - 애플리케이션 런처
프로젝트 루트에서 실행하는 진입점:
```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run
from src.main import main
main()
```

### 2. `__init__.py` 파일들 (7개)
Python 패키지 마커:
- `src/__init__.py`
- `src/core/__init__.py`
- `src/ui/__init__.py`
- `src/ui/widgets/__init__.py`
- `src/ui/dialogs/__init__.py`
- `src/utils/__init__.py`
- `src/resources/__init__.py`

### 3. `verify_setup.py` - 설정 검증 스크립트
프로젝트 구조와 의존성을 확인:
```bash
python verify_setup.py
```

### 4. `QUICKSTART.md` - 빠른 시작 가이드
새로운 사용자를 위한 간단한 가이드

### 5. `MIGRATION_GUIDE.md` - 이 문서
변경사항 및 마이그레이션 가이드

## 업데이트된 파일

### 1. `src/main.py`
**변경 전:**
```python
from core.model_manager import ModelManager
from ui.main_window import MainWindow
```

**변경 후:**
```python
from .core.model_manager import ModelManager
from .ui.main_window import MainWindow
```

### 2. `build.sh` / `build.bat`
- `uv` 설치 확인 추가
- PyInstaller 설치 시 `uv pip` 사용

### 3. `README.md`
- uv 설치 방법 추가
- 새로운 실행 방법 명시
- 프로젝트 구조 업데이트

### 4. `DISTRIBUTION.md`
- 빌드 명령어에 uv 사용

### 5. `CLAUDE.md`
- 개발 가이드에 uv 반영

## 마이그레이션 단계

기존 환경에서 새 구조로 전환하기:

### 1단계: 코드 업데이트
```bash
git pull  # 또는 새 코드 다운로드
```

### 2단계: uv 설치
```bash
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3단계: 기존 venv 제거 (선택사항)
```bash
rm -rf venv  # 기존 venv 디렉토리 제거
```

### 4단계: 새 가상환경 생성
```bash
cd deepseek_ocr_desktop
uv venv
source .venv/bin/activate  # Linux/Mac
# 또는
.venv\Scripts\activate  # Windows
```

### 5단계: 의존성 설치
```bash
uv pip install -r requirements.txt
```

### 6단계: 설정 검증
```bash
python verify_setup.py
```

### 7단계: 애플리케이션 실행
```bash
uv run run.py
# 또는
python run.py
```

## 문제 해결

### Q: ImportError: attempted relative import beyond top-level package
**A:** 반드시 프로젝트 루트에서 `run.py`를 실행하세요:
```bash
cd deepseek_ocr_desktop
python run.py  # ✅

# 이렇게 하지 마세요:
cd src
python main.py  # ❌
```

### Q: ModuleNotFoundError: No module named 'PySide6'
**A:** 의존성을 설치하세요:
```bash
uv pip install -r requirements.txt
```

### Q: uv command not found
**A:** uv를 먼저 설치하세요:
```bash
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Q: 기존 venv 디렉토리와 충돌
**A:** 기존 venv를 삭제하고 uv로 새로 생성:
```bash
rm -rf venv
uv venv
source .venv/bin/activate
```

## 호환성

### Python 버전
- Python 3.8+ 지원 (기존과 동일)

### 기존 코드
- 모든 기존 기능 정상 작동
- API 변경 없음
- 설정 파일 호환 (QSettings)

### 빌드
- PyInstaller 빌드 정상 작동
- build.sh / build.bat 자동으로 uv 사용

## 추가 리소스

- [uv 공식 문서](https://github.com/astral-sh/uv)
- [QUICKSTART.md](QUICKSTART.md) - 빠른 시작 가이드
- [README.md](README.md) - 전체 문서
- [DISTRIBUTION.md](DISTRIBUTION.md) - 빌드 및 배포

## 요약

✅ **변경사항:**
1. pip → uv로 전환
2. venv → .venv로 변경
3. Python 패키지 구조 수정 (`__init__.py` 추가)
4. `run.py` 런처 추가
5. 실행 방법 변경 (`cd src && python main.py` → `python run.py`)

✅ **장점:**
- 빠른 패키지 설치 (10-100배)
- ImportError 완전 해결
- 표준 Python 패키지 구조 준수
- 더 나은 개발 경험

✅ **실행 방법:**
```bash
cd deepseek_ocr_desktop
uv run run.py
```

🎉 **모든 변경사항 완료! 정상 작동합니다!**
