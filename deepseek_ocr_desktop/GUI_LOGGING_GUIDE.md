# GUI 로그 뷰어 사용 가이드

## 🎉 새로운 기능: GUI 내장 로그 뷰어

이제 터미널이 아닌 **애플리케이션 내에서** 모든 로그를 실시간으로 확인할 수 있습니다!

---

## 📺 GUI 로그 뷰어 위치

메인 윈도우의 **하단 패널**에 위치:

```
┌─────────────────────────────────────────────┐
│  Result Viewer (결과 보기)                   │
│                                             │
├─────────────────────────────────────────────┤
│  📋 Application Logs (애플리케이션 로그)      │  ← 여기!
│  [Filter: INFO ▼] [Auto-scroll ☑] [Clear]  │
│  ────────────────────────────────────────── │
│  [INFO    ] 14:30:45 | PDF processing...   │
│  [INFO    ] 14:30:46 | Page 1/5 - starting │
│  [DEBUG   ] 14:30:47 | OCR complete...     │
└─────────────────────────────────────────────┘
```

---

## 🎮 주요 기능

### 1. 실시간 로그 표시
- 모든 로그가 **컬러 코딩**되어 표시
- DEBUG (회색), INFO (초록), WARNING (주황), ERROR (빨강)

### 2. 레벨별 필터링
**Filter 드롭다운** 사용:
- **ALL** - 모든 로그 표시
- **DEBUG** - DEBUG 이상 (가장 상세)
- **INFO** - INFO 이상 (일반 정보)
- **WARNING** - WARNING 이상 (경고만)
- **ERROR** - ERROR 이상 (에러만)
- **CRITICAL** - CRITICAL만 (치명적 오류)

**권장 설정:**
- 일반 사용: **INFO**
- PDF 디버깅: **DEBUG**
- 문제 확인: **ERROR**

### 3. Auto-scroll
- ☑ **체크**: 새 로그가 추가되면 자동 스크롤
- ☐ **해제**: 스크롤 고정 (이전 로그 확인 시)

### 4. 버튼 기능

| 버튼 | 기능 |
|------|------|
| **🗑️ Clear** | 모든 로그 지우기 |
| **📋 Copy All** | 전체 로그 클립보드 복사 |
| **💾 Export** | 로그를 파일로 저장 |

---

## ⌨️ 키보드 단축키

### 로그 뷰어 토글
```
Ctrl + L
```
- 로그 뷰어 표시/숨김
- 화면 공간 확보가 필요할 때 유용

### 메뉴 사용
```
View → Show Logs (☑/☐)
```

---

## 🔍 PDF 디버깅 실전 가이드

### 문제: PDF output이 비어있음

#### 1단계: 로그 뷰어 열기
```
Ctrl + L  (로그 뷰어 표시)
```

#### 2단계: DEBUG 레벨로 설정
```
Filter: ALL 또는 DEBUG
```

#### 3단계: PDF 처리 시작
```
1. PDF 파일 업로드
2. "Process PDF" 버튼 클릭
3. 하단 로그 뷰어 주시
```

#### 4단계: 로그 확인
다음 메시지들을 확인:

✅ **정상 로그 예시:**
```
[INFO    ] Reading PDF file: /path/to/file.pdf
[INFO    ] PDF converted to 5 images                    ← ✓ PDF 읽기 성공
[INFO    ] PDF Page 1/5 - starting
[INFO    ] Page 1: Running OCR inference...
[INFO    ] Page 1: OCR complete - text length: 2345     ← ✓ 텍스트 추출됨!
[INFO    ] Page 1 processed successfully
[INFO    ] PDF Page 1/5 - completed
...
[INFO    ] Converting 5 pages to markdown format...
[INFO    ] Markdown conversion complete - 12345 characters ← ✓ 변환 성공!
[INFO    ] PDF processing complete!
[INFO    ]   Content size: 12345                         ← ✓ 컨텐츠 있음!
```

❌ **문제 로그 예시:**
```
[INFO    ] Page 1: OCR complete - text length: 0        ← ✗ 텍스트 없음!
[ERROR   ] Error processing page 1: ...                 ← ✗ 에러 발생!
```

#### 5단계: 문제 해결
- `text length: 0` → OCR 실패
- `ERROR` 메시지 → 스택 트레이스 확인
- 로그를 Export하여 분석 또는 이슈 제출

---

## 💡 실전 활용 팁

### Tip 1: 로그 내보내기
문제가 계속되면:
1. 문제 재현
2. "Export" 버튼 클릭
3. `deepseek_ocr_log_YYYYMMDD_HHMMSS.txt` 저장
4. GitHub Issue에 첨부

### Tip 2: 에러만 빠르게 확인
```
1. Filter를 "ERROR"로 설정
2. 빨간색 로그만 표시됨
3. 문제 빠르게 파악
```

### Tip 3: 이전 로그 확인
```
1. Auto-scroll 체크 해제 ☐
2. 스크롤바로 이전 로그 확인
3. 확인 후 다시 체크 ☑
```

### Tip 4: 로그 정리
```
처리 전에 "Clear" 버튼 클릭
→ 새로운 작업의 로그만 표시
```

---

## 📊 로그 레벨 의미

| 레벨 | 의미 | 언제 확인 |
|------|------|-----------|
| DEBUG | 상세 디버깅 정보 | 문제 분석 시 |
| INFO | 일반 작업 정보 | 정상 동작 확인 |
| WARNING | 경고 (작동은 함) | 주의 필요 |
| ERROR | 에러 (실패) | 문제 발생 |
| CRITICAL | 치명적 오류 | 심각한 문제 |

---

## 🔄 파일 로그와 GUI 로그 차이

### GUI 로그 뷰어
- ✅ 실시간 확인
- ✅ 필터링 가능
- ✅ 컬러 코딩
- ❌ 애플리케이션 종료 시 사라짐

### 파일 로그
- ✅ 영구 저장
- ✅ 터미널 명령어로 검색 가능
- ✅ 여러 실행 기록 보관
- ❌ 별도 프로그램으로 열어야 함

**권장:**
- 실시간 디버깅 → GUI 로그 뷰어
- 사후 분석 → 파일 로그

---

## 📍 로그 파일 위치

GUI에서 Export한 로그와 별개로, 자동 로그 파일도 저장됩니다:

### Linux/Mac
```bash
~/.deepseek_ocr/logs/deepseek_ocr_20251203.log
```

### Windows
```cmd
%USERPROFILE%\.deepseek_ocr\logs\deepseek_ocr_20251203.log
```

### 터미널에서 실시간 확인
```bash
# Linux/Mac
tail -f ~/.deepseek_ocr/logs/deepseek_ocr_$(date +%Y%m%d).log

# Windows PowerShell
Get-Content -Path "$env:USERPROFILE\.deepseek_ocr\logs\deepseek_ocr_*.log" -Wait -Tail 50
```

---

## ❓ FAQ

### Q: 로그가 너무 많이 쌓여요
**A:** "Clear" 버튼으로 정리하세요. 작업 전마다 클릭하면 깔끔합니다.

### Q: 로그 뷰어가 화면을 너무 차지해요
**A:**
- Ctrl+L로 숨기기
- 또는 구분선을 드래그해서 크기 조절

### Q: 특정 로그만 보고 싶어요
**A:** Filter 드롭다운 사용:
- PDF 처리 과정: DEBUG
- 에러만: ERROR
- 일반 정보: INFO

### Q: 로그를 GitHub Issue에 첨부하려면?
**A:**
1. 문제 재현
2. "Export" 버튼 클릭
3. 저장된 .txt 파일 첨부

---

## 🎯 요약

1. **Ctrl+L** - 로그 뷰어 열기/닫기
2. **Filter** - 로그 레벨 선택 (일반: INFO, 디버깅: DEBUG)
3. **Clear** - 로그 지우기 (작업 전)
4. **Export** - 로그 저장 (문제 분석 시)

**PDF 디버깅:**
- Filter를 DEBUG로 설정
- `text length: 0` 확인 → OCR 실패
- `ERROR` 메시지 확인 → 에러 발생

---

더 자세한 로그 시스템 정보는 [LOGGING_GUIDE.md](LOGGING_GUIDE.md)를 참조하세요.
