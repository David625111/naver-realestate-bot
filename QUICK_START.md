# ⚡ 빠른 실행 가이드 (5분 완료)

경험자를 위한 초간단 실행 가이드입니다.

---

## 📋 체크리스트

### 1️⃣ 텔레그램 봇 생성 (2분)
```
1. @BotFather → /newbot
2. 토큰 복사: 1234567890:ABC...
3. 봇에게 메시지 전송
4. https://api.telegram.org/bot<TOKEN>/getUpdates
5. 채팅 ID 복사: 987654321
```

### 2️⃣ 지역 코드 확인 (1분)
```
1. https://new.land.naver.com
2. 원하는 지역 검색
3. URL의 cortarNo 복사: 1168010600
```

### 3️⃣ 로컬 설정 (2분)
```powershell
# 가상환경 생성 및 활성화
python -m venv venv
.\venv\Scripts\Activate.ps1

# 패키지 설치
pip install -r requirements.txt

# .env 파일 생성
@"
TELEGRAM_BOT_TOKEN=실제_토큰
TELEGRAM_CHAT_ID=실제_채팅ID
SEARCH_REGIONS=1168010600
TRADE_TYPES=A1,B1
"@ | Out-File -FilePath .env -Encoding UTF8
```

### 4️⃣ 테스트 (30초)
```powershell
cd src
python test_basic.py
python main.py
```

---

## 🚀 GitHub Actions 자동화 (선택)

### 1️⃣ 저장소 생성
```powershell
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/naver-realestate-bot.git
git push -u origin main
```

### 2️⃣ Secrets 설정
```
Settings → Secrets → Actions → New repository secret

1. TELEGRAM_BOT_TOKEN = 1234567890:ABC...
2. TELEGRAM_CHAT_ID = 987654321
3. SEARCH_REGIONS = 1168010600,1165010100
4. TRADE_TYPES = A1,B1
```

### 3️⃣ 수동 실행 테스트
```
Actions → 네이버 부동산 크롤링 → Run workflow
```

---

## 🎯 필터 조정 (선택)

### 느슨한 설정 (매물 많음)
```json
{
  "trade_types": ["A1", "B1"],
  "price_range": {
    "A1": {"min": 0, "max": 999999},
    "B1": {"min": 0, "max": 999999}
  },
  "area_range": {"min": 0, "max": 999999},
  "approval_year": {"min": 0, "max": 9999},
  "household_count": {"min": 0, "max": 999999},
  "floor_types": [],
  "room_count": [],
  "bathroom_count": [],
  "directions": [],
  "loan": "상관없음"
}
```

---

## ⚠️ 자주 발생하는 문제

| 문제 | 해결 |
|------|------|
| 실행 정책 오류 | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| 텔레그램 알림 안 옴 | 봇 START 버튼 클릭 확인 |
| 403 에러 | 10분 후 재시도 또는 GitHub Actions 사용 |
| ModuleNotFoundError | 가상환경 활성화 확인 |
| 매물 안 나옴 | 필터 느슨하게 조정 |

---

## 📱 결과 확인

✅ **성공 신호:**
- 콘솔에 "크롤링 완료 요약" 출력
- 텔레그램으로 매물 알림 수신
- `data/properties.db` 파일 생성
- `scraper.log` 파일 생성

---

## 🔗 상세 가이드

더 자세한 내용은 [SETUP_GUIDE.md](SETUP_GUIDE.md) 참고

---

**축하합니다! 🎉 5분 안에 완료되었습니다!**
