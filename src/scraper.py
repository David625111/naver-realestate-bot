"""
네이버 부동산 크롤링 모듈
API를 통해 매물 정보 수집

✅ Selenium + requests 하이브리드 방식:
- Selenium: 메인 페이지 방문, 쿠키 획득 (실제 브라우저)
- requests: API 호출 (빠름)
"""

import requests
import random
import time
from typing import List, Dict, Optional
import logging
from datetime import datetime
import numpy as np

# Selenium 관련 임포트
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium을 사용할 수 없습니다. pip install undetected-chromedriver 설치가 필요합니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NaverRealEstateScraper:
    """네이버 부동산 크롤러 클래스"""
    
    # 브라우저별 완전한 프로파일 (Fingerprinting 우회)
    BROWSER_PROFILES = [
        # Chrome 121 (Windows) - 최신 버전
        {
            'type': 'chrome',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'sec_ch_ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec_ch_ua_mobile': '?0',
            'sec_ch_ua_platform': '"Windows"',
            'accept': 'application/json, text/plain, */*',
            'accept_language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        },
        # Chrome 120 (Windows)
        {
            'type': 'chrome',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'sec_ch_ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec_ch_ua_mobile': '?0',
            'sec_ch_ua_platform': '"Windows"',
            'accept': 'application/json, text/plain, */*',
            'accept_language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        },
        # Chrome 121 (Mac)
        {
            'type': 'chrome',
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'sec_ch_ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec_ch_ua_mobile': '?0',
            'sec_ch_ua_platform': '"macOS"',
            'accept': 'application/json, text/plain, */*',
            'accept_language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        },
        # Firefox 122 (Windows)
        {
            'type': 'firefox',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'accept': 'application/json, text/plain, */*',
            'accept_language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        },
        # Firefox 121 (Windows)
        {
            'type': 'firefox',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'accept': 'application/json, text/plain, */*',
            'accept_language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        },
        # Firefox 122 (Mac)
        {
            'type': 'firefox',
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
            'accept': 'application/json, text/plain, */*',
            'accept_language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        },
        # Edge 121 (Windows)
        {
            'type': 'edge',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            'sec_ch_ua': '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
            'sec_ch_ua_mobile': '?0',
            'sec_ch_ua_platform': '"Windows"',
            'accept': 'application/json, text/plain, */*',
            'accept_language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        },
        # Safari 17.2 (Mac)
        {
            'type': 'safari',
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept_language': 'ko-KR,ko;q=0.9',
        },
    ]
    
    BASE_URL = "https://new.land.naver.com"
    
    def __init__(self, use_selenium: bool = True):
        """
        크롤러 초기화
        
        Args:
            use_selenium: Selenium 사용 여부 (True: 실제 브라우저, False: requests만)
        """
        self.session = requests.Session()
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.driver = None  # Selenium WebDriver
        
        # ✅ 개선: 세션 시작 시 브라우저 프로필을 한 번만 선택 (핵심!)
        # 실제 사용자는 한 세션에서 브라우저를 바꾸지 않음!
        self.browser_profile = random.choice(self.BROWSER_PROFILES)
        
        self.cookies_received = False  # 쿠키 수신 여부
        self.last_cookie_refresh = time.time()  # 마지막 쿠키 갱신 시간
        
        self._set_fixed_headers()  # 헤더를 한 번만 설정
        
        # Selenium 초기화
        if self.use_selenium:
            self._init_selenium()
        
        self._visit_homepage()  # 초기 방문으로 쿠키 받기
        
        # 사람처럼 행동하기 위한 상태 관리
        self.request_count = 0  # 총 요청 횟수
        self.last_break_count = 0  # 마지막 휴식 시점
        self.session_start_time = time.time()  # 세션 시작 시간
        self.fatigue_level = 0.0  # 피로도 (0.0 ~ 1.0)
    
    def _init_selenium(self):
        """
        ✅ Selenium WebDriver 초기화 (undetected-chromedriver)
        
        실제 Chrome 브라우저를 사용하여 쿠키를 획득합니다.
        """
        try:
            logger.info("🚀 Selenium (Chrome) 초기화 중...")
            
            # undetected-chromedriver 옵션 설정
            options = uc.ChromeOptions()
            
            # 헤드리스 모드 (백그라운드 실행)
            # options.add_argument('--headless')  # 디버깅 시 주석 처리
            
            # 기타 옵션
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(f'user-agent={self.browser_profile["user_agent"]}')
            
            # WebDriver 생성
            self.driver = uc.Chrome(options=options, version_main=None)
            
            logger.info("✅ Selenium 초기화 완료!")
            
        except Exception as e:
            logger.error(f"❌ Selenium 초기화 실패: {e}")
            logger.warning("⚠️  requests 모드로 전환합니다.")
            self.use_selenium = False
            self.driver = None
    
    def _visit_homepage(self):
        """
        ✅ 네이버 부동산 홈페이지 방문 (쿠키 받기)
        
        Selenium 사용 시: 실제 브라우저로 방문하여 JavaScript 실행 → 쿠키 획득!
        requests 사용 시: 기존 방식 (쿠키 획득 실패 가능)
        """
        if self.use_selenium and self.driver:
            # ✅ Selenium으로 메인 페이지 방문 (쿠키 획득 성공!)
            try:
                logger.info("🌐 Selenium으로 네이버 부동산 메인 페이지 방문 중...")
                
                self.driver.get(self.BASE_URL)
                
                # 페이지 로딩 대기 (최대 10초)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 쿠키 획득 및 requests Session에 전달
                selenium_cookies = self.driver.get_cookies()
                
                if selenium_cookies:
                    for cookie in selenium_cookies:
                        self.session.cookies.set(cookie['name'], cookie['value'])
                    
                    self.cookies_received = True
                    self.last_cookie_refresh = time.time()
                    logger.info(f"✅ 쿠키 수신 성공: {len(selenium_cookies)}개")
                    
                    # 주요 쿠키 로깅
                    cookie_names = [c['name'] for c in selenium_cookies]
                    important_cookies = ['NNB', 'JSESSIONID', 'nid_inf', 'NID_AUT', 'NID_SES']
                    found_cookies = [key for key in important_cookies if key in cookie_names]
                    if found_cookies:
                        logger.info(f"🍪 주요 쿠키 확인: {', '.join(found_cookies)}")
                else:
                    logger.warning("⚠️  쿠키를 받지 못했습니다.")
                
                time.sleep(random.uniform(2, 4))
                logger.info("✅ Selenium 초기 방문 완료 (세션 준비됨)")
                
            except Exception as e:
                logger.error(f"❌ Selenium 방문 실패: {e}")
                logger.warning("⚠️  requests 모드로 전환합니다.")
                self.use_selenium = False
        
        else:
            # ❌ requests만 사용 (쿠키 획득 실패 가능)
            try:
                logger.info("🌐 네이버 부동산 메인 페이지 방문 중 (requests)...")
                
                # Accept 헤더를 HTML 페이지용으로 변경
                original_accept = self.session.headers.get('Accept', '')
                self.session.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
                
                # 메인 페이지 방문
                response = self.session.get(self.BASE_URL, timeout=10)
                
                # 쿠키 수신 확인
                cookies = self.session.cookies.get_dict()
                if cookies:
                    self.cookies_received = True
                    self.last_cookie_refresh = time.time()
                    logger.info(f"✅ 쿠키 수신 성공: {len(cookies)}개")
                else:
                    logger.warning("⚠️  쿠키를 받지 못했습니다. 차단될 가능성 높음!")
                
                # Accept 헤더 복원
                if original_accept:
                    self.session.headers['Accept'] = original_accept
                
                time.sleep(random.uniform(2, 4))
                logger.info("✅ 초기 방문 완료 (세션 준비됨)")
                
            except Exception as e:
                logger.warning(f"❌ 초기 방문 실패: {e}")
    
    def _set_fixed_headers(self):
        """
        ✅ 개선: 세션 시작 시 브라우저 정보를 한 번만 설정 (핵심!)
        
        실제 사용자는 한 세션 내에서 브라우저를 바꾸지 않습니다.
        동일한 쿠키를 가진 유저가 매 요청마다 브라우저를 바꾸면
        서버는 즉시 봇으로 인식합니다!
        """
        profile = self.browser_profile
        browser_type = profile['type']
        
        # 기본 헤더 (모든 브라우저 공통)
        headers = {
            'Host': 'new.land.naver.com',  # 명시적 설정 (중요!)
            'User-Agent': profile['user_agent'],
            'Accept': profile['accept'],
            'Accept-Language': profile['accept_language'],
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://new.land.naver.com/',
            'Origin': 'https://new.land.naver.com',
            'Connection': 'keep-alive',
            'DNT': '1',  # Do Not Track
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        
        # Chrome/Edge 전용 헤더 (Sec-Fetch-*, sec-ch-ua)
        if browser_type in ['chrome', 'edge']:
            headers.update({
                'sec-ch-ua': profile['sec_ch_ua'],
                'sec-ch-ua-mobile': profile['sec_ch_ua_mobile'],
                'sec-ch-ua-platform': profile['sec_ch_ua_platform'],
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
            })
        
        # Firefox 전용 헤더
        elif browser_type == 'firefox':
            headers.update({
                'TE': 'trailers',  # Firefox 고유
            })
        
        # Safari 전용 헤더
        elif browser_type == 'safari':
            # Safari는 sec-ch-ua 없음
            pass
        
        self.session.headers.clear()
        self.session.headers.update(headers)
        
        logger.info(f"🌐 브라우저 프로파일 고정: {browser_type.upper()}")
        logger.info(f"   User-Agent: {profile['user_agent'][:80]}...")
    
    def _human_like_delay(self, base_min_minutes: float = 0.5, base_max_minutes: float = 1.5) -> float:
        """
        ✅ 개선: 2배 빠른 속도로 조정 (1-3분 → 0.5-1.5분)
        
        사람처럼 불규칙한 대기 시간 생성 (정규분포 사용)
        
        Args:
            base_min_minutes: 최소 대기 시간 (분)
            base_max_minutes: 최대 대기 시간 (분)
            
        Returns:
            실제 대기 시간 (초)
        """
        # 정규분포로 더 자연스러운 랜덤성
        mean = (base_min_minutes + base_max_minutes) / 2
        std = (base_max_minutes - base_min_minutes) / 4
        delay_minutes = np.random.normal(mean, std)
        
        # 최소/최대 범위 내로 제한
        delay_minutes = max(base_min_minutes, min(base_max_minutes, delay_minutes))
        
        # 피로도 반영 (시간이 지날수록 느려짐)
        delay_minutes *= (1 + self.fatigue_level * 0.5)
        
        # 활동 시간대 반영 (낮 시간 vs 밤 시간)
        hour = datetime.now().hour
        if 9 <= hour <= 18:  # 오전 9시 ~ 오후 6시 (활발)
            delay_minutes *= 0.8
        elif hour >= 22 or hour <= 6:  # 밤 10시 ~ 새벽 6시 (느림)
            delay_minutes *= 1.3
        
        # 분을 초로 변환
        return delay_minutes * 60
    
    def _should_take_break(self) -> bool:
        """
        휴식이 필요한지 판단 (사람처럼 불규칙하게)
        
        Returns:
            True if 휴식 필요
        """
        requests_since_break = self.request_count - self.last_break_count
        
        # 5-10개 요청마다 휴식 (랜덤)
        break_threshold = random.randint(5, 10)
        
        if requests_since_break >= break_threshold:
            # 80% 확률로 휴식 (완전히 예측 불가능하게)
            return random.random() < 0.8
        
        # 가끔 갑자기 휴식 (5% 확률)
        return random.random() < 0.05
    
    def _take_break(self):
        """
        ✅ 개선: 2배 빠른 휴식 시간 (10-30분 → 5-15분)
        
        긴 휴식 시간 (사람이 커피 마시거나 점심 먹는 시간)
        """
        # 베타 분포로 더 자연스러운 휴식 시간 (5분~15분, 평균 10분)
        alpha, beta = 2, 2
        normalized = np.random.beta(alpha, beta)
        break_minutes = 5 + normalized * 10  # 5~15분 (2배 빠름!)
        break_seconds = break_minutes * 60
        
        self.last_break_count = self.request_count
        
        logger.info(f"☕ 장시간 휴식 (커피/간식): {break_minutes:.1f}분 ({break_seconds:.0f}초) 대기...")
        logger.info(f"   (총 {self.request_count}개 요청 완료, 피로도: {self.fatigue_level:.2f})")
        
        time.sleep(break_seconds)
        
        # 휴식 후 피로도 감소
        self.fatigue_level = max(0, self.fatigue_level - 0.2)
    
    def _simulate_reading(self):
        """
        ✅ 개선: requests에서는 마우스/스크롤이 의미 없으므로 단순 지연으로 변경
        
        페이지를 읽는 시간 시뮬레이션 (초 단위로 2배 빠르게!)
        """
        # 감마 분포로 읽기 시간 (30초~150초, 평균 75초)
        # 기존: 1-5분 → 개선: 0.5-2.5분 (2배 빠름!)
        reading_seconds = np.random.gamma(2, 1.5) * 30
        reading_seconds = min(150, max(30, reading_seconds))
        reading_minutes = reading_seconds / 60
        
        logger.info(f"📖 페이지 읽는 중... {reading_minutes:.1f}분 ({reading_seconds:.0f}초)")
        time.sleep(reading_seconds)
    
    def _update_fatigue(self):
        """
        피로도 업데이트 (시간이 지날수록 증가)
        """
        session_duration = (time.time() - self.session_start_time) / 3600  # 시간 단위
        self.fatigue_level = min(1.0, session_duration * 0.1)  # 10시간 후 최대
    
    def _check_and_refresh_cookies(self):
        """
        쿠키 유효성 검사 및 필요시 재방문
        
        네이버 쿠키는 시간이 지나면 만료될 수 있으므로,
        일정 시간(30분)마다 메인 페이지를 다시 방문하여 쿠키를 갱신합니다.
        """
        # 30분(1800초)마다 쿠키 갱신
        cookie_lifetime = 1800  # 30분
        current_time = time.time()
        
        if not self.cookies_received or (current_time - self.last_cookie_refresh) > cookie_lifetime:
            logger.info("🔄 쿠키 만료 또는 미수신 → 메인 페이지 재방문...")
            self._visit_homepage()
    
    def _visit_landing_page(self, page_type: str):
        """
        ✅ API 호출 전에 해당 페이지를 먼저 방문 (랜딩 페이지 전략)
        
        Selenium 사용 시: 실제 브라우저로 방문하여 쿠키 갱신
        requests 사용 시: 기존 방식
        
        Args:
            page_type: 'complexes' (단지 목록), 'complex' (단지 상세), 'articles' (매물 목록)
        """
        landing_urls = {
            'complexes': 'https://new.land.naver.com/complexes',
            'complex': 'https://new.land.naver.com/complexes',
            'articles': 'https://new.land.naver.com/articles',
        }
        
        landing_url = landing_urls.get(page_type, self.BASE_URL)
        
        if self.use_selenium and self.driver:
            # ✅ Selenium으로 페이지 방문 (쿠키 갱신)
            try:
                logger.info(f"🚪 Selenium으로 랜딩 페이지 방문: {landing_url}")
                
                self.driver.get(landing_url)
                
                # 페이지 로딩 대기
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 쿠키 갱신
                selenium_cookies = self.driver.get_cookies()
                for cookie in selenium_cookies:
                    self.session.cookies.set(cookie['name'], cookie['value'])
                
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                logger.warning(f"⚠️  Selenium 랜딩 페이지 방문 실패: {e}")
        
        else:
            # ❌ requests로 페이지 방문
            try:
                logger.info(f"🚪 랜딩 페이지 방문: {landing_url}")
                
                # Accept 헤더를 HTML 페이지용으로 변경
                original_accept = self.session.headers.get('Accept', '')
                self.session.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
                
                # 페이지 방문
                self.session.get(landing_url, timeout=10)
                
                # Accept 헤더 복원 (API 요청용)
                if original_accept:
                    self.session.headers['Accept'] = original_accept
                
                # 짧은 대기 (0.5-1.5초)
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                logger.warning(f"⚠️  랜딩 페이지 방문 실패: {e}")
    
    def _get_referer_for_url(self, url: str) -> str:
        """
        URL에 따라 적절한 Referer 반환 (Referer 체인)
        
        Args:
            url: 요청 URL
            
        Returns:
            적절한 Referer URL
        """
        if '/api/complexes' in url:
            # 단지 검색 API → 메인 페이지에서 온 것처럼
            return 'https://new.land.naver.com/'
        elif '/api/articles/complex/' in url:
            # 매물 목록 API → 단지 페이지에서 온 것처럼
            return 'https://new.land.naver.com/complexes'
        elif '/api/articles/' in url:
            # 매물 상세 API → 매물 목록에서 온 것처럼
            return 'https://new.land.naver.com/articles'
        else:
            # 기본값
            return 'https://new.land.naver.com/'
    
    def _safe_request(self, url: str, params: Dict = None, retry: int = 3) -> Optional[Dict]:
        """
        안전한 HTTP 요청 (재시도 포함, 429 에러 특별 처리, 사람처럼 행동)
        
        Args:
            url: 요청 URL
            params: 쿼리 파라미터
            retry: 재시도 횟수
            
        Returns:
            JSON 응답 또는 None
        """
        # 쿠키 유효성 검사 및 갱신
        self._check_and_refresh_cookies()
        
        # 요청 전 휴식 필요 여부 확인
        if self._should_take_break():
            self._take_break()
        
        for attempt in range(retry):
            try:
                # ✅ 개선: User-Agent는 세션 시작 시 한 번만 설정했으므로 여기서 변경하지 않음!
                # Referer만 URL에 맞게 동적으로 변경합니다.
                referer = self._get_referer_for_url(url)
                self.session.headers['Referer'] = referer
                
                # 쿠키 상태 로깅 (디버깅용)
                if self.request_count % 10 == 0:  # 10번마다
                    cookies_count = len(self.session.cookies.get_dict())
                    logger.info(f"🍪 현재 쿠키 수: {cookies_count}개")
                
                # ✅ 개선: 2배 빠른 대기 시간 (1-3분 → 0.5-1.5분)
                if attempt == 0:
                    delay = self._human_like_delay(0.5, 1.5)  # 0.5-1.5분 (2배 빠름!)
                    delay_minutes = delay / 60
                    logger.info(f"🤔 생각하는 중... {delay_minutes:.1f}분 ({delay:.0f}초)")
                    time.sleep(delay)
                
                # 요청 카운트 증가 및 피로도 업데이트
                self.request_count += 1
                self._update_fatigue()
                
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    # 성공 시 페이지 읽기 시뮬레이션 (30% 확률)
                    if random.random() < 0.3:
                        self._simulate_reading()
                    return response.json()
                
                elif response.status_code == 429:
                    # 429 Too Many Requests - 30분 대기!
                    wait_minutes = 30
                    wait_seconds = wait_minutes * 60
                    
                    logger.warning(f"⚠️  429 에러 (Too Many Requests) 발생!")
                    logger.info(f"🚨 크롤링 차단 감지 - {wait_minutes}분 ({wait_seconds}초) 대기...")
                    logger.info(f"   현재 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info(f"   재개 예정: {(datetime.now().timestamp() + wait_seconds)}")
                    
                    if attempt < retry - 1:
                        logger.info(f"🕐 {wait_minutes}분 휴식 후 재시도 예정 ({attempt + 2}/{retry})")
                        time.sleep(wait_seconds)
                        self._update_headers()  # User-Agent 변경
                        logger.info("✅ 휴식 완료. 크롤링 재개...")
                    else:
                        logger.error("❌ 최대 재시도 횟수 초과. 프로그램을 나중에 다시 실행하세요.")
                        return None
                
                elif response.status_code == 403:
                    # 403 Forbidden
                    logger.warning(f"접근 거부 (403). 헤더 변경 후 재시도... ({attempt + 1}/{retry})")
                    self._update_headers()
                    delay = random.uniform(5, 10)
                    time.sleep(delay)
                
                else:
                    logger.warning(f"응답 코드 {response.status_code}")
                    if attempt < retry - 1:
                        delay = random.uniform(3, 7)
                        time.sleep(delay)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"요청 오류: {e}")
                if attempt < retry - 1:
                    delay = random.uniform(5, 10)
                    logger.info(f"오류 후 {delay:.1f}초 대기...")
                    time.sleep(delay)
        
        return None
    
    def search_complexes(self, cortarNo: str, trade_type: str = "A1") -> List[Dict]:
        """
        지역별 단지 검색
        
        Args:
            cortarNo: 지역 코드 (예: 1168010600 - 강남구 대치동)
            trade_type: 거래 유형 (A1: 매매, B1: 전세, B2: 월세, B3: 단기임대)
            
        Returns:
            단지 정보 리스트
        """
        # API 호출 전 랜딩 페이지 먼저 방문 (중요!)
        self._visit_landing_page('complexes')
        
        url = f"{self.BASE_URL}/api/complexes"
        
        params = {
            'cortarNo': cortarNo,
            'realEstateType': 'APT:OPST',  # 아파트, 오피스텔
            'tradeType': trade_type,
            'tag': '::::::::',
            'rentPriceMin': 0,
            'rentPriceMax': 999999,
            'priceMin': 0,
            'priceMax': 999999,
            'areaMin': 0,
            'areaMax': 999999,
            'oldBuildYears': '',
            'recentlyBuildYears': '',
            'minHouseHoldCount': '',
            'maxHouseHoldCount': '',
            'showArticle': 'false',
            'sameAddressGroup': 'true',
            'page': 1,
            'complexNo': '',
            'buildingNo': ''
        }
        
        logger.info(f"단지 검색: cortarNo={cortarNo}, tradeType={trade_type}")
        data = self._safe_request(url, params)
        
        if data and 'complexList' in data:
            complexes = data['complexList']
            logger.info(f"검색된 단지 수: {len(complexes)}")
            return complexes
        
        logger.warning("단지 검색 실패")
        return []
    
    def get_complex_articles(self, complex_no: str, trade_type: str = "A1") -> List[Dict]:
        """
        특정 단지의 매물 목록 가져오기
        
        Args:
            complex_no: 단지 번호
            trade_type: 거래 유형
            
        Returns:
            매물 정보 리스트
        """
        # API 호출 전 랜딩 페이지 먼저 방문 (중요!)
        self._visit_landing_page('complex')
        
        url = f"{self.BASE_URL}/api/articles/complex/{complex_no}"
        
        params = {
            'realEstateType': 'APT:OPST',
            'tradeType': trade_type,
            'tag': '::::::::',
            'rentPriceMin': 0,
            'rentPriceMax': 999999,
            'priceMin': 0,
            'priceMax': 999999,
            'areaMin': 0,
            'areaMax': 999999,
            'oldBuildYears': '',
            'recentlyBuildYears': '',
            'minHouseHoldCount': '',
            'maxHouseHoldCount': '',
            'showArticle': 'true',
            'sameAddressGroup': 'false',
            'minMoveInMonth': '',
            'maxMoveInMonth': '',
            'page': 1
        }
        
        logger.info(f"매물 검색: complexNo={complex_no}")
        data = self._safe_request(url, params)
        
        if data and 'articleList' in data:
            articles = data['articleList']
            logger.info(f"검색된 매물 수: {len(articles)}")
            
            # ✅ 개선: 2배 빠른 대기 시간 (2-5분 → 1-2.5분)
            delay = self._human_like_delay(1.0, 2.5)  # 1-2.5분 (2배 빠름!)
            delay_minutes = delay / 60
            logger.info(f"🕒 매물 목록 확인 중... {delay_minutes:.1f}분 ({delay:.0f}초)")
            time.sleep(delay)
            
            return articles
        
        logger.warning(f"매물 검색 실패: complexNo={complex_no}")
        return []
    
    def get_article_detail(self, article_no: str) -> Optional[Dict]:
        """
        매물 상세 정보 가져오기
        
        Args:
            article_no: 매물 번호
            
        Returns:
            매물 상세 정보
        """
        url = f"{self.BASE_URL}/api/articles/{article_no}"
        
        logger.info(f"매물 상세 정보: articleNo={article_no}")
        data = self._safe_request(url)
        
        # ✅ 개선: 2배 빠른 대기 시간 (1-3분 → 0.5-1.5분)
        delay = self._human_like_delay(0.5, 1.5)  # 0.5-1.5분 (2배 빠름!)
        delay_minutes = delay / 60
        logger.info(f"📄 상세 정보 읽는 중... {delay_minutes:.1f}분 ({delay:.0f}초)")
        time.sleep(delay)
        
        return data
    
    def scrape_region(self, cortarNo: str, trade_types: List[str] = ["A1"]) -> List[Dict]:
        """
        특정 지역의 모든 매물 크롤링
        
        Args:
            cortarNo: 지역 코드
            trade_types: 거래 유형 리스트
            
        Returns:
            모든 매물 정보 리스트
        """
        all_properties = []
        
        for idx, trade_type in enumerate(trade_types):
            logger.info(f"=== 거래 유형 {trade_type} 크롤링 시작 ===")
            logger.info(f"📊 진행 상황: {idx + 1}/{len(trade_types)}, 총 요청: {self.request_count}회, 피로도: {self.fatigue_level:.2f}")
            
            # ✅ 개선: 2배 빠른 거래 전환 휴식 (30-60분 → 15-30분)
            if idx > 0:
                long_delay = self._human_like_delay(15.0, 30.0)  # 15-30분 (2배 빠름!)
                long_delay_minutes = long_delay / 60
                logger.info(f"🔄 거래 유형 전환 휴식: {long_delay_minutes:.1f}분 ({long_delay:.0f}초)")
                time.sleep(long_delay)
            
            # 1. 단지 목록 가져오기
            complexes = self.search_complexes(cortarNo, trade_type)
            
            # 순서 무작위화 (Shuffle) - 사람처럼 불규칙하게!
            if complexes:
                random.shuffle(complexes)
                logger.info(f"🔀 단지 순서 무작위화 완료 (총 {len(complexes)}개)")
            
            # 2. 각 단지의 매물 가져오기
            for i, complex_info in enumerate(complexes[:10], 1):  # 테스트: 상위 10개만
                complex_no = complex_info.get('complexNo')
                complex_name = complex_info.get('complexName', '알 수 없음')
                
                logger.info(f"[{i}/{len(complexes[:10])}] {complex_name} (complexNo: {complex_no})")
                
                # ✅ 개선: requests에서는 마우스 시뮬레이션이 의미 없으므로 제거
                
                articles = self.get_complex_articles(complex_no, trade_type)
                
                # 매물 순서도 무작위화 (Shuffle)
                if articles:
                    random.shuffle(articles)
                    logger.info(f"🔀 매물 순서 무작위화 완료 (총 {len(articles)}개)")
                
                for article in articles:
                    # 매물 데이터 가공
                    property_data = self._parse_article(article, complex_info, trade_type)
                    all_properties.append(property_data)
                
                # ✅ 개선: 2배 빠른 단지 이동 (5-10분 → 2.5-5분)
                delay = self._human_like_delay(2.5, 5.0)  # 2.5-5분 (2배 빠름!)
                delay_minutes = delay / 60
                logger.info(f"🏢 다음 단지로 이동... {delay_minutes:.1f}분 ({delay:.0f}초)")
                time.sleep(delay)
                
                # ✅ 개선: 2배 빠른 추가 휴식 (15-30분 → 7.5-15분)
                if random.random() < 0.2:
                    long_break_minutes = random.uniform(7.5, 15)
                    long_break_seconds = long_break_minutes * 60
                    logger.info(f"💤 추가 장시간 휴식: {long_break_minutes:.1f}분 ({long_break_seconds:.0f}초)")
                    time.sleep(long_break_seconds)
        
        logger.info(f"총 {len(all_properties)}개 매물 크롤링 완료")
        return all_properties
    
    def _parse_article(self, article: Dict, complex_info: Dict, trade_type: str) -> Dict:
        """
        매물 데이터 파싱
        
        Args:
            article: 매물 원본 데이터
            complex_info: 단지 정보
            trade_type: 거래 유형
            
        Returns:
            파싱된 매물 정보
        """
        article_no = article.get('articleNo', '')
        complex_no = complex_info.get('complexNo', '')
        
        return {
            'id': f"{complex_no}_{article_no}",
            'complex_no': complex_no,
            'complex_name': complex_info.get('complexName', ''),
            'article_no': article_no,
            'price': article.get('dealOrWarrantPrc', 0),  # 매매가 또는 전세가
            'area_real': article.get('area1', 0),  # 공급면적
            'area_exclusive': article.get('area2', 0),  # 전용면적
            'floor': article.get('floorInfo', ''),
            'total_floors': complex_info.get('maxFloor', 0),
            'direction': article.get('direction', ''),
            'trade_type': trade_type,
            'approval_year': complex_info.get('useApproveYmd', '')[:4] if complex_info.get('useApproveYmd') else 0,
            'household_count': complex_info.get('totalHouseholdCount', 0),
            'room_count': article.get('roomCnt', 0),
            'bathroom_count': article.get('bathroomCnt', 0),
            'loan_amount': article.get('loanAmount', 0),
            'description': article.get('tagList', []),
            'url': f"https://new.land.naver.com/complexes/{complex_no}?articleNo={article_no}"
        }


    def __del__(self):
        """소멸자: Selenium WebDriver 종료"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("✅ Selenium WebDriver 종료됨")
            except:
                pass


if __name__ == "__main__":
    # 테스트 코드
    scraper = NaverRealEstateScraper(use_selenium=True)  # ✅ Selenium 사용!
    
    # 강남구 대치동 지역 코드
    cortarNo = "1168010600"
    
    try:
        properties = scraper.scrape_region(cortarNo, trade_types=["B1"])
        
        print(f"\n크롤링 완료: {len(properties)}개 매물")
        if properties:
            print("\n첫 번째 매물 예시:")
            print(properties[0])
    
    finally:
        # Selenium 종료
        if scraper.driver:
            scraper.driver.quit()
