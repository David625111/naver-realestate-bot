# 네이버 부동산 크롤링 텔레그램 봇 🏠

네이버 부동산에서 2시간마다 신규 매물을 자동으로 크롤링하여 텔레그램으로 알림을 보내주는 봇입니다.

## ✨ 주요 기능

- 🔍 **자동 크롤링**: 2시간마다 네이버 부동산 API에서 매물 정보 수집
- 🎯 **맞춤 필터**: 11가지 조건으로 원하는 매물만 필터링
- 📱 **텔레그램 알림**: 신규 매물 발견 시 즉시 알림
- 💾 **중복 제거**: 이미 본 매물은 다시 알림하지 않음
- 🆓 **완전 무료**: GitHub Actions로 서버 비용 없이 운영

## 🎯 필터 조건

1. **물건 유형**: 아파트, 오피스텔
2. **거래 방식**: 매매, 전세, 월세, 단기임대
3. **가격대**: 최소~최대 가격 설정
4. **면적**: 평수 범위 지정
5. **사용승인일**: 건물 연식 제한
6. **세대수**: 단지 규모
7. **층수**: 저층, 중간층, 고층, 탑층
8. **방/욕실 수**: 원하는 구조
9. **방향**: 남향, 동남향 등
10. **융자금**: 융자 비율 제한
11. **기타 옵션**: 올수리, 복층 등

## 📋 사전 준비

### 1. 텔레그램 봇 생성

1. 텔레그램에서 [@BotFather](https://t.me/BotFather) 검색
2. `/newbot` 명령어 입력
3. 봇 이름과 사용자명 설정
4. 받은 **토큰** 저장 (예: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. 채팅 ID 확인

1. 생성한 봇과 대화 시작 (아무 메시지나 전송)
2. 브라우저에서 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` 접속
3. `"chat":{"id":` 뒤의 숫자가 **채팅 ID** (예: `123456789`)

### 3. 지역 코드 찾기

네이버 부동산에서 원하는 지역 검색 후 URL의 `cortarNo` 값 복사:
- 예: `https://new.land.naver.com/complexes?cortarNo=1168010600`
- 이 경우 지역 코드는 `1168010600` (강남구 대치동)

## 🚀 설치 및 설정

### 1. 저장소 생성

1. GitHub에서 **New Repository** 클릭
2. 저장소 이름 입력 (예: `naver-realestate-bot`)
3. **Public**으로 설정 (GitHub Actions 무료 사용)
4. Create repository

### 2. 코드 업로드

```bash
# 프로젝트 폴더로 이동
cd naver-realestate-bot

# Git 초기화
git init
git add .
git commit -m "Initial commit: 네이버 부동산 크롤링 봇"

# GitHub에 업로드
git remote add origin https://github.com/YOUR_USERNAME/naver-realestate-bot.git
git branch -M main
git push -u origin main
```

### 3. GitHub Secrets 설정

저장소 Settings → Secrets and variables → Actions → New repository secret

다음 4개의 Secret 추가:

| Name | Value | 설명 |
|------|-------|------|
| `TELEGRAM_BOT_TOKEN` | `1234567890:ABC...` | 텔레그램 봇 토큰 |
| `TELEGRAM_CHAT_ID` | `123456789` | 채팅 ID |
| `SEARCH_REGIONS` | `1168010600,1165010100` | 검색할 지역 코드 (쉼표로 구분) |
| `TRADE_TYPES` | `A1,B1` | 거래 유형 (A1:매매, B1:전세) |

### 4. 필터 설정

`config/filters.json` 파일을 수정하여 원하는 조건 설정:

```json
{
  "property_types": ["APT", "OPST"],
  "trade_types": ["A1", "B1"],
  "price_range": {
    "A1": {"min": 50000, "max": 150000},
    "B1": {"min": 30000, "max": 80000}
  },
  "area_range": {"min": 59, "max": 84},
  "approval_year": {"min": 2018, "max": 2024},
  "household_count": {"min": 300, "max": 2000},
  "floor_types": ["중간층", "고층"],
  "room_count": [2, 3],
  "bathroom_count": [2],
  "directions": ["남향", "남동향", "남서향"],
  "loan": "상관없음"
}
```

수정 후 커밋:

```bash
git add config/filters.json
git commit -m "Update: 필터 설정 변경"
git push
```

## 🔧 로컬 테스트

### 1. 가상환경 생성 및 패키지 설치

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일 생성:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
SEARCH_REGIONS=1168010600
TRADE_TYPES=A1,B1
```

### 3. 실행

```bash
cd src
python main.py
```

## 📊 실행 확인

### GitHub Actions에서 확인

1. 저장소의 **Actions** 탭 클릭
2. 최신 워크플로우 실행 확인
3. 로그에서 크롤링 결과 확인

### 수동 실행

1. Actions 탭 → "네이버 부동산 크롤링" 선택
2. **Run workflow** 클릭
3. 즉시 크롤링 시작

### 텔레그램 알림 예시

```
🏠 새 매물 발견!

📌 단지명: 래미안 강남파크팰리스
💰 거래: 매매 13억 5천만원
📐 면적: 84.5㎡ (전용 59.2㎡)
🏢 층수: 15/25
🧭 방향: 남향
📅 승인: 2020년 (6년차)
🏘 세대수: 850세대

🔗 https://new.land.naver.com/complexes/12345?articleNo=67890
```

## 🗂️ 프로젝트 구조

```
naver-realestate-bot/
├── .github/
│   └── workflows/
│       └── scraper.yml          # GitHub Actions 설정
├── src/
│   ├── main.py                  # 메인 실행 파일
│   ├── scraper.py               # 네이버 API 크롤링
│   ├── filter_manager.py        # 필터링 로직
│   ├── database.py              # SQLite 데이터베이스
│   └── telegram_bot.py          # 텔레그램 알림
├── config/
│   └── filters.json             # 필터 설정
├── data/
│   └── properties.db            # 매물 데이터베이스
├── requirements.txt             # Python 패키지
├── .env.example                 # 환경 변수 예시
├── .gitignore
└── README.md
```

## 🔧 트러블슈팅

### 크롤링이 안 돼요

1. **403 에러**: 네이버에서 차단한 경우
   - GitHub Actions는 IP가 자주 바뀌므로 보통 문제없음
   - 계속 발생 시 실행 주기를 3시간으로 변경

2. **API 구조 변경**: 네이버가 API를 변경한 경우
   - Issues에 문제 제보
   - 코드 업데이트 필요

### 텔레그램 알림이 안 와요

1. Secrets 설정 확인
2. 봇과 대화를 먼저 시작했는지 확인
3. Actions 로그에서 에러 메시지 확인

### 너무 많은 알림이 와요

`config/filters.json`에서 조건을 더 엄격하게 설정:
- 가격 범위 좁히기
- 면적 범위 좁히기
- 층수, 방향 등 추가 조건 설정

## 📝 주의사항

1. **공개 저장소 필수**: GitHub Actions 무료 사용을 위해 Public 저장소 사용
2. **Secrets 보안**: 토큰과 ID는 절대 코드에 하드코딩하지 마세요
3. **크롤링 빈도**: 너무 자주 실행하면 IP 차단 가능성
4. **데이터베이스 크기**: 매물이 많아지면 정기적으로 정리 필요

## 🛠️ 향후 개발 계획

- [ ] 웹 대시보드 (GitHub Pages)
- [ ] 가격 변동 추적
- [ ] 멀티 유저 지원
- [ ] 카카오톡 알림 추가

## 📄 라이선스

MIT License - 자유롭게 사용하세요!

## 🙋‍♂️ 문의

문제가 있거나 개선 아이디어가 있다면 [Issues](https://github.com/YOUR_USERNAME/naver-realestate-bot/issues)에 남겨주세요.

---

⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!
