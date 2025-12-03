# Changelog: uv Integration & Import Fix

## 날짜: 2025-12-03

## 변경 요약

DeepSeek-OCR Desktop 애플리케이션을 `uv` 기반으로 전환하고, ImportError 문제를 완전히 해결했습니다.

---

## 🎯 해결된 문제

### 1. ImportError 완전 해결
**문제:**
```
ImportError: attempted relative import beyond top-level package
```

**원인:**
- `src/` 디렉토리가 Python 패키지로 인식되지 않음
- `cd src && python main.py` 실행 시 상대 임포트 실패

**해결:**
- ✅ 7개의 `__init__.py` 파일 추가하여 패키지 구조 완성
- ✅ `run.py` 런처 생성으로 올바른 실행 경로 제공
- ✅ `main.py`의 임포트를 상대 임포트로 변경

### 2. uv 통합
**변경 전:**
```bash
python -m venv venv
pip install -r requirements.txt
```

**변경 후:**
```bash
uv venv
uv pip install -r requirements.txt
```

**장점:**
- 10-100배 빠른 패키지 설치
- Rust 기반 고성능
- 완벽한 pip 호환성

---

## 📁 새로 추가된 파일

### 1. `run.py` (애플리케이션 런처)
프로젝트 루트에서 앱을 올바르게 실행하는 진입점
```bash
python run.py
# 또는
uv run run.py
```

### 2. Python 패키지 마커들
```
src/__init__.py
src/core/__init__.py
src/ui/__init__.py
src/ui/widgets/__init__.py
src/ui/dialogs/__init__.py
src/utils/__init__.py
src/resources/__init__.py
```

### 3. `verify_setup.py` (설정 검증 스크립트)
프로젝트 구조와 의존성을 자동으로 확인
```bash
python verify_setup.py
```
출력 예:
```
🔍 Verifying DeepSeek-OCR Desktop setup...

✓ Checking project structure...
  ✅ All required files present

✓ Checking Python package structure...
  ✅ src package importable

✓ Checking dependencies...
  ✅ PySide6 installed
  ✅ torch installed
  ...
```

### 4. 문서 파일들
- **QUICKSTART.md**: 빠른 시작 가이드
- **MIGRATION_GUIDE.md**: 상세한 마이그레이션 가이드
- **CHANGELOG_UV.md**: 이 문서

---

## 🔧 수정된 파일

### 1. `src/main.py`
**변경:**
```python
# Before
from core.model_manager import ModelManager
from ui.main_window import MainWindow

# After
from .core.model_manager import ModelManager
from .ui.main_window import MainWindow
```

**이유:** 상대 임포트로 통일하여 패키지 구조 준수

### 2. `build.sh` / `build.bat`
**변경:**
- `uv` 설치 여부 확인 추가
- PyInstaller 설치 시 `uv pip install` 사용

### 3. 문서 업데이트
- **README.md**: uv 설치 및 실행 방법 추가
- **DISTRIBUTION.md**: 빌드 가이드에 uv 반영
- **CLAUDE.md**: 개발 가이드 업데이트

---

## 🚀 새로운 실행 방법

### ✅ 올바른 방법
```bash
cd deepseek_ocr_desktop

# 방법 1: uv run (권장)
uv run run.py

# 방법 2: Python 직접 실행
python run.py

# 방법 3: 가상환경 활성화 후
source .venv/bin/activate
python run.py
```

### ❌ 잘못된 방법 (더 이상 작동하지 않음)
```bash
cd src
python main.py  # ImportError 발생!
```

---

## 📋 설치 가이드 (신규 사용자)

### 1단계: uv 설치
```bash
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2단계: 가상환경 생성 및 의존성 설치
```bash
cd deepseek_ocr_desktop
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### 3단계: 설정 검증 (선택사항)
```bash
python verify_setup.py
```

### 4단계: 애플리케이션 실행
```bash
uv run run.py
```

---

## 🔄 마이그레이션 (기존 사용자)

### 간단한 방법
```bash
# 1. 기존 venv 제거
rm -rf venv

# 2. uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. 새 가상환경 생성
uv venv

# 4. 의존성 설치
source .venv/bin/activate
uv pip install -r requirements.txt

# 5. 실행
uv run run.py
```

자세한 내용은 [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) 참조

---

## 🎨 프로젝트 구조 (업데이트)

```
deepseek_ocr_desktop/
├── run.py                      # ✨ 애플리케이션 런처 (NEW)
├── verify_setup.py             # ✨ 설정 검증 스크립트 (NEW)
├── QUICKSTART.md               # ✨ 빠른 시작 가이드 (NEW)
├── MIGRATION_GUIDE.md          # ✨ 마이그레이션 가이드 (NEW)
├── CHANGELOG_UV.md             # ✨ 이 문서 (NEW)
├── src/
│   ├── __init__.py             # ✨ 패키지 마커 (NEW)
│   ├── main.py                 # 🔧 임포트 수정 (UPDATED)
│   ├── core/
│   │   ├── __init__.py         # ✨ (NEW)
│   │   └── ...
│   ├── ui/
│   │   ├── __init__.py         # ✨ (NEW)
│   │   ├── widgets/
│   │   │   ├── __init__.py     # ✨ (NEW)
│   │   │   └── ...
│   │   └── dialogs/
│   │       ├── __init__.py     # ✨ (NEW)
│   │       └── ...
│   ├── utils/
│   │   ├── __init__.py         # ✨ (NEW)
│   │   └── ...
│   └── resources/
│       ├── __init__.py         # ✨ (NEW)
│       └── ...
├── build.sh                    # 🔧 uv 지원 추가 (UPDATED)
├── build.bat                   # 🔧 uv 지원 추가 (UPDATED)
├── README.md                   # 🔧 문서 업데이트 (UPDATED)
├── DISTRIBUTION.md             # 🔧 문서 업데이트 (UPDATED)
└── requirements.txt
```

---

## 🧪 테스트 결과

### Import 구조 테스트
```bash
$ python verify_setup.py
✅ All required files present
✅ src package importable
```

### 실행 테스트
```bash
$ uv run run.py
# 정상 실행 확인 ✅
```

---

## 📚 추가 리소스

- **빠른 시작**: [QUICKSTART.md](QUICKSTART.md)
- **마이그레이션**: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- **전체 문서**: [README.md](README.md)
- **빌드 가이드**: [DISTRIBUTION.md](DISTRIBUTION.md)
- **개발 가이드**: [../CLAUDE.md](../CLAUDE.md)
- **uv 공식 문서**: https://github.com/astral-sh/uv

---

## ✅ 체크리스트

설치 및 실행 전 확인사항:

- [ ] uv 설치 완료
- [ ] 프로젝트 루트 디렉토리에 위치 (`deepseek_ocr_desktop/`)
- [ ] 가상환경 생성 (`uv venv`)
- [ ] 가상환경 활성화
- [ ] 의존성 설치 (`uv pip install -r requirements.txt`)
- [ ] (선택) 설정 검증 (`python verify_setup.py`)
- [ ] 애플리케이션 실행 (`uv run run.py`)

---

## 🎉 요약

**핵심 변경사항:**
1. ✅ ImportError 완전 해결
2. ✅ uv 통합으로 10-100배 빠른 설치
3. ✅ 표준 Python 패키지 구조 준수
4. ✅ 새로운 `run.py` 런처
5. ✅ 자동 검증 스크립트 (`verify_setup.py`)
6. ✅ 완벽한 문서화

**실행 방법:**
```bash
uv run run.py
```

**모든 기능 정상 작동! 🚀**
