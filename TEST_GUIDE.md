# 로컬 테스트 가이드

## 사전 준비

### 1. 텔레그램 봇 생성
1. 텔레그램에서 @BotFather 검색
2. `/newbot` 명령어 실행
3. 봇 이름과 사용자명 설정
4. 받은 토큰 저장

### 2. 채팅 ID 확인
1. 생성한 봇과 대화 시작
2. 웹 브라우저에서 접속:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
3. "chat":{"id": 뒤의 숫자가 채팅 ID

## 로컬 테스트 단계

### 1단계: 가상환경 생성
```bash
python -m venv venv
```

### 2단계: 가상환경 활성화
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat
```

### 3단계: 패키지 설치
```bash
pip install -r requirements.txt
```

### 4단계: .env 파일 생성
`.env.example` 파일을 복사하여 `.env` 파일 생성:
```bash
copy .env.example .env
```

그리고 실제 값으로 수정:
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
SEARCH_REGIONS=1168010600
TRADE_TYPES=A1
```

### 5단계: 모듈 테스트
```bash
cd src
python test_modules.py
```

### 6단계: 메인 프로그램 실행
```bash
cd src
python main.py
```

## 예상 결과

### 정상 실행 시
```
============================================================
부동산 크롤링 시작
실행 시간: 2026-01-27 20:00:00
============================================================

[지역 크롤링] cortarNo: 1168010600
단지 검색: cortarNo=1168010600, tradeType=A1
검색된 단지 수: 50

...

============================================================
크롤링 완료 요약
============================================================
전체 크롤링 매물: 150개
필터 통과 매물: 20개
신규 매물: 20개
알림 전송: 20개
```

## 문제 해결

### 403 Forbidden 에러
네이버 API 차단 시 발생. 잠시 후 재시도하거나 VPN 사용.

### 텔레그램 알림 안 옴
1. 봇과 대화 시작했는지 확인 (START 클릭)
2. .env 파일의 토큰과 ID 확인
3. 웹 API로 테스트:
   ```
   https://api.telegram.org/bot<TOKEN>/sendMessage?chat_id=<CHAT_ID>&text=테스트
   ```

### 매물이 너무 많음
`config/filters.json`에서 필터 조건 강화
