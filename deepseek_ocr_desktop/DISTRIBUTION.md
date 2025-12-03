# DeepSeek-OCR Desktop - Distribution Guide

배포용 실행 파일 생성 및 배포 가이드

## 빌드 방법

### 사전 요구사항

**시스템 요구사항:**
- NVIDIA GPU with CUDA support
- 16GB+ RAM (모델 로딩용)
- 20GB+ 디스크 공간 (빌드 + 모델)

**소프트웨어 요구사항:**
- Python 3.8+
- CUDA 11.8+ with NVIDIA drivers
- [uv](https://github.com/astral-sh/uv) - 빠른 Python 패키지 관리자
  ```bash
  # uv 설치 (Linux/Mac)
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # uv 설치 (Windows)
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- 모든 requirements.txt 의존성 설치됨

### Linux/Mac 빌드

```bash
# 1. 저장소로 이동
cd deepseek_ocr_desktop

# 2. 가상 환경 생성 및 활성화
uv venv
source .venv/bin/activate

# 3. 의존성 설치
uv pip install -r requirements.txt

# 4. 빌드 실행
./build.sh
```

빌드가 완료되면 `dist/DeepSeek-OCR/` 디렉토리에 실행 파일이 생성됩니다.

### Windows 빌드

```cmd
REM 1. 저장소로 이동
cd deepseek_ocr_desktop

REM 2. 가상 환경 생성 및 활성화
uv venv
.venv\Scripts\activate

REM 3. 의존성 설치
uv pip install -r requirements.txt

REM 4. 빌드 실행
build.bat
```

빌드가 완료되면 `dist\DeepSeek-OCR\` 디렉토리에 실행 파일이 생성됩니다.

## 빌드 결과물

### 디렉토리 구조

```
dist/DeepSeek-OCR/
├── DeepSeek-OCR          # 실행 파일 (Linux/Mac)
├── DeepSeek-OCR.exe      # 실행 파일 (Windows)
├── resources/
│   └── styles/
│       └── app.qss       # 스타일시트
├── _internal/            # PyInstaller 라이브러리들
│   ├── PySide6/
│   ├── torch/
│   ├── transformers/
│   └── ... (기타 의존성)
└── ... (기타 파일들)
```

### 예상 크기

- **실행 파일 디렉토리**: ~1.5-2.5GB
  - PyTorch + CUDA: ~1GB
  - PySide6: ~200MB
  - Transformers: ~100MB
  - 기타 의존성: ~200-500MB

- **모델 파일**: ~5-10GB (별도, 첫 실행 시 다운로드)
  - 위치: `~/.cache/huggingface/` (Linux/Mac)
  - 위치: `%USERPROFILE%\.cache\huggingface\` (Windows)

**총 필요 공간**: 약 7-13GB

## 배포 패키징

### Linux 배포

```bash
cd dist
tar -czf DeepSeek-OCR-linux-x64.tar.gz DeepSeek-OCR/
```

생성된 파일: `DeepSeek-OCR-linux-x64.tar.gz`

### Windows 배포

1. `dist\DeepSeek-OCR` 폴더를 마우스 오른쪽 클릭
2. "보내기 → 압축(ZIP) 폴더" 선택
3. 파일명: `DeepSeek-OCR-windows-x64.zip`

또는 7-Zip 사용:
```cmd
7z a DeepSeek-OCR-windows-x64.7z dist\DeepSeek-OCR\
```

### Mac 배포

```bash
cd dist
tar -czf DeepSeek-OCR-macos-x64.tar.gz DeepSeek-OCR/
```

## 사용자 설치 가이드

### Linux 사용자

1. **압축 해제**
   ```bash
   tar -xzf DeepSeek-OCR-linux-x64.tar.gz
   cd DeepSeek-OCR
   ```

2. **실행**
   ```bash
   ./DeepSeek-OCR
   ```

3. **첫 실행 시**
   - 모델 다운로드: ~5-10GB (시간이 걸릴 수 있음)
   - HuggingFace 캐시: `~/.cache/huggingface/`

### Windows 사용자

1. **압축 해제**
   - `DeepSeek-OCR-windows-x64.zip` 파일을 압축 해제
   - 원하는 위치에 폴더 배치 (예: `C:\Program Files\DeepSeek-OCR\`)

2. **실행**
   - `DeepSeek-OCR.exe` 더블클릭

3. **첫 실행 시**
   - 모델 다운로드: ~5-10GB (시간이 걸릴 수 있음)
   - HuggingFace 캐시: `%USERPROFILE%\.cache\huggingface\`

4. **바탕화면 바로가기 생성 (선택사항)**
   - `DeepSeek-OCR.exe`를 마우스 오른쪽 클릭
   - "바로가기 만들기" 선택
   - 바로가기를 바탕화면으로 이동

### Mac 사용자

1. **압축 해제**
   ```bash
   tar -xzf DeepSeek-OCR-macos-x64.tar.gz
   cd DeepSeek-OCR
   ```

2. **실행 권한 부여**
   ```bash
   chmod +x DeepSeek-OCR
   ```

3. **실행**
   ```bash
   ./DeepSeek-OCR
   ```

4. **첫 실행 시**
   - 모델 다운로드: ~5-10GB
   - "확인되지 않은 개발자" 경고가 나타날 수 있습니다
   - 시스템 환경설정 → 보안 및 개인 정보 보호 → "확인 없이 열기"

## 문제 해결

### 빌드 오류

**"ModuleNotFoundError" 발생**
- 해결: `pip install -r requirements.txt` 재실행
- 모든 의존성이 설치되었는지 확인

**"PyInstaller not found"**
- 해결: `pip install pyinstaller>=6.0.0`

**빌드는 성공했지만 실행 시 오류**
- `deepseek_ocr.spec` 파일의 `hiddenimports` 섹션 확인
- 누락된 모듈 추가

### 실행 오류

**"CUDA not available"**
- NVIDIA 드라이버 설치 확인: `nvidia-smi`
- CUDA Toolkit 설치 확인
- GPU 지원 PyTorch 설치 확인

**"Model download failed"**
- 인터넷 연결 확인
- HuggingFace 접근 가능 여부 확인
- 디스크 공간 확인 (~10GB 필요)

**실행 파일이 너무 느림**
- 첫 실행은 모델 로딩으로 느릴 수 있음 (5-30초)
- GPU가 없으면 실행 불가능 (CUDA 필수)

### Linux 특정 오류

**"libxcb-xinerama.so.0: cannot open shared object file"**
- 해결: `sudo apt-get install libxcb-xinerama0`

**"qt.qpa.plugin: Could not load the Qt platform plugin"**
- 해결: `export QT_QPA_PLATFORM=xcb`

### Windows 특정 오류

**"VCRUNTIME140.dll not found"**
- Microsoft Visual C++ Redistributable 설치 필요
- https://aka.ms/vs/17/release/vc_redist.x64.exe

**바이러스 경고**
- PyInstaller 실행 파일은 가끔 오탐될 수 있음
- 안티바이러스에 예외 추가 또는 무시

## 업데이트 방법

### 사용자용

1. 기존 설치 폴더 삭제
2. 새 버전 다운로드 및 압축 해제
3. 모델 캐시는 유지됨 (`~/.cache/huggingface/`)

### 개발자용

1. 코드 변경 후 새로 빌드:
   ```bash
   ./build.sh  # Linux/Mac
   build.bat   # Windows
   ```

2. 버전 번호 업데이트:
   - `src/ui/main_window.py`의 `show_about()` 메서드

## 라이선스 및 배포

- 이 프로젝트는 DeepSeek-OCR 모델을 사용합니다
- 배포 시 원본 라이선스 준수 필요
- 모델 파일은 사용자가 직접 다운로드 (배포 패키지에 미포함)

## 지원

문제가 발생하면:
1. 이 문서의 "문제 해결" 섹션 확인
2. GitHub Issues 등록
3. 로그 파일 첨부 (있는 경우)
