"""
네이버 부동산 크롤링 모듈
API를 통해 매물 정보 수집
"""

import requests
import random
import time
from typing import List, Dict, Optional
import logging
from datetime import datetime
import numpy as np

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
    
    def __init__(self):
        """크롤러 초기화"""
        self.session = requests.Session()
        self.current_browser_profile = None  # 현재 브라우저 프로파일
        self.cookies_received = False  # 쿠키 수신 여부
        self.last_cookie_refresh = time.time()  # 마지막 쿠키 갱신 시간
        
        self._update_headers()
        self._visit_homepage()  # 초기 방문으로 쿠키 받기
        
        # 사람처럼 행동하기 위한 상태 관리
        self.request_count = 0  # 총 요청 횟수
        self.last_break_count = 0  # 마지막 휴식 시점
        self.session_start_time = time.time()  # 세션 시작 시간
        self.fatigue_level = 0.0  # 피로도 (0.0 ~ 1.0)
    
    def _visit_homepage(self):
        """
        네이버 부동산 홈페이지 방문 (쿠키 받기)
        실제 브라우저처럼 동작하기 위해
        
        중요: 이 과정에서 NNB, JSESSIONID 등 네이버 쿠키를 받아야 합니다!
        """
        try:
            logger.info("🌐 네이버 부동산 메인 페이지 방문 중 (쿠키 수신)...")
            
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
                
                # 주요 쿠키 로깅 (NNB, JSESSIONID 등)
                important_cookies = ['NNB', 'JSESSIONID', 'nid_inf', 'NID_AUT', 'NID_SES']
                found_cookies = [key for key in important_cookies if key in cookies]
                if found_cookies:
                    logger.info(f"🍪 주요 쿠키 확인: {', '.join(found_cookies)}")
                else:
                    logger.warning("⚠️  주요 쿠키(NNB, JSESSIONID)를 찾지 못했습니다.")
            else:
                logger.warning("⚠️  쿠키를 받지 못했습니다. 차단될 가능성 높음!")
            
            # Accept 헤더 복원
            if original_accept:
                self.session.headers['Accept'] = original_accept
            
            time.sleep(random.uniform(2, 4))
            logger.info("✅ 초기 방문 완료 (세션 준비됨)")
            
        except Exception as e:
            logger.warning(f"❌ 초기 방문 실패: {e}")
    
    def _update_headers(self):
        """
        요청 헤더 업데이트 (Fingerprinting 완벽 우회)
        브라우저별로 완전히 다른 헤더 프로파일 사용
        """
        # 브라우저 프로파일 무작위 선택
        self.current_browser_profile = random.choice(self.BROWSER_PROFILES)
        browser_type = self.current_browser_profile['type']
        
        # 기본 헤더 (모든 브라우저 공통)
        headers = {
            'Host': 'new.land.naver.com',  # 명시적 설정 (중요!)
            'User-Agent': self.current_browser_profile['user_agent'],
            'Accept': self.current_browser_profile['accept'],
            'Accept-Language': self.current_browser_profile['accept_language'],
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
                'sec-ch-ua': self.current_browser_profile['sec_ch_ua'],
                'sec-ch-ua-mobile': self.current_browser_profile['sec_ch_ua_mobile'],
                'sec-ch-ua-platform': self.current_browser_profile['sec_ch_ua_platform'],
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
        
        logger.info(f"🌐 브라우저 프로파일 변경: {browser_type.upper()} - {self.current_browser_profile['user_agent'][:50]}...")
    
    def _human_like_delay(self, base_min_minutes: float = 1.0, base_max_minutes: float = 3.0) -> float:
        """
        사람처럼 불규칙한 대기 시간 생성 (분 단위, 정규분포 사용)
        
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
        긴 휴식 시간 (사람이 커피 마시거나 점심 먹는 시간) - 분 단위
        """
        # 베타 분포로 더 자연스러운 휴식 시간 (10분~30분, 평균 20분)
        alpha, beta = 2, 2
        normalized = np.random.beta(alpha, beta)
        break_minutes = 10 + normalized * 20  # 10~30분
        break_seconds = break_minutes * 60
        
        self.last_break_count = self.request_count
        
        logger.info(f"☕ 장시간 휴식 (점심/커피): {break_minutes:.1f}분 ({break_seconds:.0f}초) 대기...")
        logger.info(f"   (총 {self.request_count}개 요청 완료, 피로도: {self.fatigue_level:.2f})")
        
        time.sleep(break_seconds)
        
        # 휴식 후 피로도 감소
        self.fatigue_level = max(0, self.fatigue_level - 0.2)
    
    def _simulate_mouse_movement(self):
        """
        마우스 움직임 시뮬레이션 (특정 좌표로 부드럽게 이동)
        """
        # 마우스를 여러 단계로 나눠 부드럽게 이동 (5-10단계)
        steps = random.randint(5, 10)
        
        logger.info(f"🖱️  마우스 움직임 시뮬레이션 ({steps}단계)...")
        
        for i in range(steps):
            # 각 단계마다 0.1~0.5초 대기
            step_delay = random.uniform(0.1, 0.5)
            time.sleep(step_delay)
    
    def _simulate_scroll(self):
        """
        페이지 스크롤 시뮬레이션 (위아래 불규칙하게)
        """
        # 스크롤 횟수 (2-5회)
        scroll_count = random.randint(2, 5)
        
        logger.info(f"📜 페이지 스크롤 시뮬레이션 ({scroll_count}회)...")
        
        for i in range(scroll_count):
            # 각 스크롤마다 0.3~1.0초 대기
            scroll_delay = random.uniform(0.3, 1.0)
            time.sleep(scroll_delay)
            
            # 가끔 위로 스크롤 (20% 확률)
            if random.random() < 0.2:
                logger.info(f"   ↑ 위로 스크롤")
            else:
                logger.info(f"   ↓ 아래로 스크롤")
    
    def _simulate_reading(self):
        """
        페이지를 읽는 시간 시뮬레이션 (스크롤, 클릭 등) - 분 단위
        """
        # 마우스 움직임 + 스크롤 + 읽기
        self._simulate_mouse_movement()
        self._simulate_scroll()
        
        # 감마 분포로 읽기 시간 (1분~5분, 평균 2.5분)
        reading_minutes = np.random.gamma(2, 1.5)
        reading_minutes = min(5, max(1, reading_minutes))
        reading_seconds = reading_minutes * 60
        
        logger.info(f"📖 매물 상세 읽는 중... {reading_minutes:.1f}분 ({reading_seconds:.0f}초)")
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
        API 호출 전에 해당 페이지를 먼저 방문 (랜딩 페이지 전략)
        
        Args:
            page_type: 'complexes' (단지 목록), 'complex' (단지 상세), 'articles' (매물 목록)
        """
        landing_urls = {
            'complexes': 'https://new.land.naver.com/complexes',
            'complex': 'https://new.land.naver.com/complexes',
            'articles': 'https://new.land.naver.com/articles',
        }
        
        landing_url = landing_urls.get(page_type, self.BASE_URL)
        
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
                # 요청마다 User-Agent 변경 (다양한 브라우저 사용)
                self._update_headers()
                
                # URL에 맞는 Referer 설정
                referer = self._get_referer_for_url(url)
                self.session.headers['Referer'] = referer
                
                # 쿠키 상태 로깅 (디버깅용)
                if self.request_count % 10 == 0:  # 10번마다
                    cookies_count = len(self.session.cookies.get_dict())
                    logger.info(f"🍪 현재 쿠키 수: {cookies_count}개")
                
                # 사람처럼 불규칙한 대기 (분 단위, 정규분포)
                if attempt == 0:
                    delay = self._human_like_delay(1.0, 3.0)  # 1-3분
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
            
            # 페이지 스크롤 시뮬레이션
            self._simulate_scroll()
            
            # 사람처럼 불규칙한 대기 (2분~5분, 정규분포)
            delay = self._human_like_delay(2.0, 5.0)  # 2-5분
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
        
        # 사람처럼 상세 정보 읽기 (1분~3분, 정규분포)
        delay = self._human_like_delay(1.0, 3.0)  # 1-3분
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
            
            # 거래 유형 간 Long Sleep (2번째부터, 30분~60분)
            if idx > 0:
                long_delay = self._human_like_delay(30.0, 60.0)  # 30-60분
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
                
                # 마우스 클릭 전 움직임 시뮬레이션
                self._simulate_mouse_movement()
                
                articles = self.get_complex_articles(complex_no, trade_type)
                
                # 매물 순서도 무작위화 (Shuffle)
                if articles:
                    random.shuffle(articles)
                    logger.info(f"🔀 매물 순서 무작위화 완료 (총 {len(articles)}개)")
                
                for article in articles:
                    # 매물 데이터 가공
                    property_data = self._parse_article(article, complex_info, trade_type)
                    all_properties.append(property_data)
                
                # 단지 간 Long Sleep (5분~10분)
                delay = self._human_like_delay(5.0, 10.0)  # 5-10분
                delay_minutes = delay / 60
                logger.info(f"🏢 다음 단지로 이동... {delay_minutes:.1f}분 ({delay:.0f}초)")
                time.sleep(delay)
                
                # 가끔 추가 Long Sleep (20% 확률로 15~30분 휴식)
                if random.random() < 0.2:
                    long_break_minutes = random.uniform(15, 30)
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


if __name__ == "__main__":
    # 테스트 코드
    scraper = NaverRealEstateScraper()
    
    # 강남구 대치동 지역 코드
    cortarNo = "1168010600"
    
    properties = scraper.scrape_region(cortarNo, trade_types=["A1"])
    
    print(f"\n크롤링 완료: {len(properties)}개 매물")
    if properties:
        print("\n첫 번째 매물 예시:")
        print(properties[0])
