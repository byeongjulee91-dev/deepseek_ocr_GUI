# 로깅 시스템 가이드

DeepSeek-OCR Desktop 애플리케이션의 로깅 시스템 사용 가이드입니다.

## 📍 로그 파일 위치

로그 파일은 사용자 홈 디렉토리의 `.deepseek_ocr/logs/` 폴더에 저장됩니다:

### Linux/Mac
```bash
~/.deepseek_ocr/logs/
```

### Windows
```cmd
%USERPROFILE%\.deepseek_ocr\logs\
```

### 로그 파일 형식
```
deepseek_ocr_YYYYMMDD.log
```

예: `deepseek_ocr_20251203.log`

---

## 🔍 로그 보기

### 방법 1: 실시간 로그 확인 (Linux/Mac)
```bash
tail -f ~/.deepseek_ocr/logs/deepseek_ocr_$(date +%Y%m%d).log
```

### 방법 2: 전체 로그 보기
```bash
# Linux/Mac
cat ~/.deepseek_ocr/logs/deepseek_ocr_$(date +%Y%m%d).log

# Windows
type %USERPROFILE%\.deepseek_ocr\logs\deepseek_ocr_YYYYMMDD.log
```

### 방법 3: 로그 디렉토리 열기
```bash
# Linux
xdg-open ~/.deepseek_ocr/logs/

# Mac
open ~/.deepseek_ocr/logs/

# Windows
explorer %USERPROFILE%\.deepseek_ocr\logs\
```

---

## 📊 로그 레벨

로그는 다음 레벨로 분류됩니다:

| 레벨 | 설명 | 예시 |
|------|------|------|
| **DEBUG** | 상세한 디버깅 정보 | 함수 호출, 변수 값, 내부 상태 |
| **INFO** | 일반 정보 | 애플리케이션 시작, 페이지 처리 완료 |
| **WARNING** | 경고 메시지 | 처리 취소, 누락된 파일 |
| **ERROR** | 에러 메시지 | 처리 실패, 예외 발생 |
| **CRITICAL** | 치명적 오류 | 애플리케이션 충돌 |

---

## 📝 로그 형식

### 파일 로그 (상세)
```
2025-12-03 14:30:45 | INFO     | DeepSeekOCR.pdf_processor:54 | __init__ | PDFWorker initialized for: /path/to/file.pdf
```

구성:
- **타임스탬프**: `2025-12-03 14:30:45`
- **레벨**: `INFO`
- **모듈**: `DeepSeekOCR.pdf_processor`
- **라인**: `:54`
- **함수**: `__init__`
- **메시지**: `PDFWorker initialized for: /path/to/file.pdf`

### 콘솔 로그 (간략, 컬러)
```
14:30:45 | INFO     | DeepSeekOCR.pdf_processor | PDFWorker initialized for: /path/to/file.pdf
```

---

## 🔎 PDF 처리 디버깅

PDF 처리 시 다음과 같은 로그가 생성됩니다:

### 1. 초기화
```
INFO | PDFWorker initialized for: /path/to/document.pdf
DEBUG | Parameters: {'output_format': 'markdown', 'dpi': 144, ...}
```

### 2. PDF 읽기 및 변환
```
INFO | Reading PDF file: /path/to/document.pdf
DEBUG | PDF file size: 1234567 bytes
INFO | Converting PDF to images at 144 DPI...
INFO | PDF converted to 5 images
```

### 3. 페이지별 처리
```
INFO | PDF Page 1/5 - starting
DEBUG | Page 1 dimensions: 1024x1448
INFO | Page 1: Running OCR inference...
INFO | Page 1: OCR complete - text length: 2345
DEBUG | Page 1: Parsed 3 bounding boxes
INFO | Page 1 processed successfully - text length: 2345
INFO | PDF Page 1/5 - completed
```

### 4. 포맷 변환
```
INFO | Converting 5 pages to markdown format...
DEBUG | Converting to Markdown...
INFO | Markdown conversion complete - 12345 characters
```

### 5. 완료
```
INFO | ============================================================
INFO | PDF processing complete!
INFO |   Total pages: 5
INFO |   Output format: markdown
INFO |   Content size: 12345
INFO |   Extracted images: 2
INFO | ============================================================
```

---

## 🐛 문제 해결

### Q: 로그 파일이 생성되지 않음
**A:** 권한 확인:
```bash
ls -la ~/.deepseek_ocr/
```

디렉토리가 없으면 자동 생성되어야 하지만, 수동으로 생성:
```bash
mkdir -p ~/.deepseek_ocr/logs
```

### Q: 로그가 너무 많음
**A:** 로그 레벨을 INFO로 변경 (`src/main.py`):
```python
logger = setup_logger("DeepSeekOCR", level=20)  # INFO level
```

레벨 코드:
- `10` = DEBUG (가장 상세)
- `20` = INFO (일반)
- `30` = WARNING (경고만)
- `40` = ERROR (에러만)

### Q: PDF output이 비어있음
**A:** 로그 파일에서 다음을 확인:
1. `OCR complete - text length: X` - OCR이 텍스트를 추출했는지
2. `Converting to X format...` - 포맷 변환이 시작되었는지
3. `Content size: X` - 최종 컨텐츠 크기

예시 분석:
```bash
# OCR 결과 확인
grep "OCR complete" ~/.deepseek_ocr/logs/deepseek_ocr_*.log

# 변환 결과 확인
grep "conversion complete" ~/.deepseek_ocr/logs/deepseek_ocr_*.log

# 에러 확인
grep "ERROR" ~/.deepseek_ocr/logs/deepseek_ocr_*.log
```

### Q: 특정 페이지만 실패
**A:** 페이지별 로그 확인:
```bash
grep "Page 3" ~/.deepseek_ocr/logs/deepseek_ocr_*.log
```

실패 원인:
- `Page 3 processing failed` - OCR 실패
- `Error processing page 3` - 예외 발생

---

## 📋 유용한 로그 명령어

### 에러만 보기
```bash
grep "ERROR" ~/.deepseek_ocr/logs/deepseek_ocr_*.log
```

### 특정 PDF 파일 처리 로그
```bash
grep "document.pdf" ~/.deepseek_ocr/logs/deepseek_ocr_*.log
```

### 처리 시간 분석
```bash
grep "processing complete" ~/.deepseek_ocr/logs/deepseek_ocr_*.log
```

### 최근 50줄 보기
```bash
tail -n 50 ~/.deepseek_ocr/logs/deepseek_ocr_$(date +%Y%m%d).log
```

### 로그 검색 (Linux/Mac)
```bash
# PDF 변환 관련 로그만
grep -i "converting to" ~/.deepseek_ocr/logs/deepseek_ocr_*.log

# 특정 시간대 로그 (14시)
grep "14:" ~/.deepseek_ocr/logs/deepseek_ocr_*.log
```

---

## 🔧 로그 설정 커스터마이징

### 로그 레벨 변경
`src/main.py` 파일 수정:

```python
# DEBUG (모든 로그)
logger = setup_logger("DeepSeekOCR", level=10)

# INFO (일반 정보만)
logger = setup_logger("DeepSeekOCR", level=20)

# WARNING (경고만)
logger = setup_logger("DeepSeekOCR", level=30)

# ERROR (에러만)
logger = setup_logger("DeepSeekOCR", level=40)
```

### 로그 파일 크기 제한
`src/utils/logger.py`의 `RotatingFileHandler` 설정:

```python
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB (기본값)
    backupCount=5,               # 백업 파일 5개 유지
    encoding='utf-8'
)
```

### 로그 파일 보관 주기
- 현재: 하루 단위 (`deepseek_ocr_YYYYMMDD.log`)
- 파일당 최대 10MB
- 최대 5개 백업 파일 유지
- 총 최대 용량: ~60MB

---

## 🎯 디버깅 워크플로우

PDF output이 비어있을 때:

1. **로그 파일 열기**:
   ```bash
   tail -f ~/.deepseek_ocr/logs/deepseek_ocr_$(date +%Y%m%d).log
   ```

2. **애플리케이션 실행 및 PDF 처리**

3. **로그에서 확인할 것**:
   - ✅ `PDF converted to X images` - PDF 읽기 성공
   - ✅ `Page X: OCR complete` - 각 페이지 OCR 성공
   - ✅ `text length: X` - 텍스트가 추출되었는지 (0이 아닌지)
   - ✅ `Converting to X format` - 포맷 변환 시작
   - ✅ `X conversion complete` - 변환 완료
   - ✅ `Content size: X` - 최종 컨텐츠 크기

4. **문제 발견 시**:
   - `ERROR` 메시지 찾기
   - 전체 스택 트레이스 확인
   - 해당 라인 번호로 코드 확인

---

## 📞 지원

문제가 해결되지 않으면:

1. 로그 파일 전체 복사
2. 문제 상황 재현 단계 기록
3. GitHub Issue에 첨부

로그 파일 경로:
```bash
~/.deepseek_ocr/logs/deepseek_ocr_YYYYMMDD.log
```
