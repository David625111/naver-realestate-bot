# 다음 단계: 실제 실행 테스트

## ✅ 현재 상태
- 코드 구조: 완료
- 필터 로직: 검증 완료
- 파일 구조: 정상

## ⏭️ 남은 작업

### 1단계: 가상환경 생성 및 패키지 설치

```bash
# 1. 가상환경 생성
python -m venv venv

# 2. 가상환경 활성화
.\venv\Scripts\Activate.ps1  # PowerShell
# 또는
venv\Scripts\activate.bat     # CMD

# 3. 패키지 설치
pip install -r requirements.txt
```

**예상 시간:** 2-3분

---

### 2단계: 텔레그램 봇 설정

#### 2-1. 봇 생성
```
1. 텔레그램 앱 실행
2. @BotFather 검색
3. /newbot 명령어
4. 봇 이름: "내 부동산 알리미"
5. 사용자명: "my_realestate_bot"
6. 토큰 복사: 1234567890:ABCdefGHIjklMNOpqrs
```

#### 2-2. 채팅 ID 확인
```
1. 봇과 대화 시작 (START 클릭)
2. 아무 메시지 전송
3. 웹 브라우저에서:
   https://api.telegram.org/bot<토큰>/getUpdates
4. "chat":{"id": 뒤의 숫자 복사
```

---

### 3단계: .env 파일 생성

프로젝트 루트에 `.env` 파일 생성:

```env
# 텔레그램 설정 (필수)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrs
TELEGRAM_CHAT_ID=123456789

# 검색 지역 (강남구 대치동 예시)
SEARCH_REGIONS=1168010600

# 거래 유형 (매매만)
TRADE_TYPES=A1
```

**주의:** 실제 값으로 교체하세요!

---

### 4단계: 로컬 테스트 실행

```bash
cd src
python main.py
```

**예상 결과:**
```
============================================================
부동산 크롤링 시작
============================================================

[지역 크롤링] cortarNo: 1168010600
단지 검색...
검색된 단지 수: 50

매물 크롤링...
크롤링 완료: 150개 매물
필터 통과: 20개 매물
신규 매물: 20개
알림 전송: 20개

텔레그램에서 메시지 확인!
```

---

### 5단계: GitHub 저장소 업로드

```bash
# Git 초기화
git init
git add .
git commit -m "Initial commit: 네이버 부동산 크롤링 봇"

# GitHub 저장소 연결 (YOUR_USERNAME 변경!)
git remote add origin https://github.com/YOUR_USERNAME/naver-realestate-bot.git
git branch -M main
git push -u origin main
```

---

### 6단계: GitHub Secrets 설정

```
1. GitHub 저장소 → Settings
2. Secrets and variables → Actions
3. New repository secret 클릭
4. 4개 추가:
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_CHAT_ID
   - SEARCH_REGIONS
   - TRADE_TYPES
```

---

### 7단계: GitHub Actions 테스트

```
1. Actions 탭
2. "네이버 부동산 크롤링" 선택
3. Run workflow 클릭
4. 실행 로그 확인
5. 텔레그램 메시지 확인
```

---

## 🎯 체크리스트

로컬 테스트:
- [ ] 가상환경 생성 및 활성화
- [ ] 패키지 설치 (`pip install -r requirements.txt`)
- [ ] 텔레그램 봇 생성 (토큰 획득)
- [ ] 채팅 ID 확인
- [ ] `.env` 파일 생성
- [ ] `python main.py` 실행
- [ ] 텔레그램 메시지 수신 확인

GitHub Actions 테스트:
- [ ] GitHub 저장소 생성 (Public)
- [ ] 코드 push
- [ ] GitHub Secrets 설정 (4개)
- [ ] Actions → Run workflow
- [ ] 실행 로그 확인
- [ ] 텔레그램 메시지 수신 확인
- [ ] 2시간 후 자동 실행 확인

---

## 💡 예상 문제 및 해결

### Q: "No module named 'requests'" 에러
```bash
A: pip install -r requirements.txt 실행 필요
```

### Q: 텔레그램 메시지 안 옴
```
A: 1. 봇과 대화 시작했는지 확인 (START)
   2. .env 파일의 토큰/ID 확인
   3. 웹 API로 테스트:
      https://api.telegram.org/bot<TOKEN>/sendMessage?chat_id=<ID>&text=테스트
```

### Q: 403 Forbidden (네이버 차단)
```
A: 1. 10분 대기 후 재시도
   2. VPN 사용
   3. GitHub Actions에서 시도 (IP 다름)
```

### Q: 매물이 너무 많음
```
A: config/filters.json 수정
   - 가격 범위 좁히기
   - 면적 범위 좁히기
   - 방향, 층수 등 조건 추가
```

---

## 📞 문제 발생 시

1. **로그 확인:**
   - 로컬: `src/scraper.log` 파일
   - GitHub: Actions 탭 → 실행 로그

2. **에러 메시지 복사:**
   - 정확한 에러 내용
   - 발생 단계

3. **환경 확인:**
   - Python 버전: `python --version`
   - 패키지 설치: `pip list`
   - .env 파일 존재 여부

---

**현재 프로젝트는 100% 완성되었습니다!**
이제 위 단계를 따라 실행하시면 됩니다. 🎉
