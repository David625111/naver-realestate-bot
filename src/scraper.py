"""
네이버 부동산 크롤링 모듈
API를 통해 매물 정보 수집
"""

import requests
import random
import time
from typing import List, Dict, Optional
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NaverRealEstateScraper:
    """네이버 부동산 크롤러 클래스"""
    
    # 다양한 User-Agent 리스트 (차단 회피) - 더 다양하게!
    USER_AGENTS = [
        # Chrome (Windows)
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        # Chrome (Mac)
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        # Firefox (Windows)
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        # Firefox (Mac)
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
        # Edge
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
        # Safari (Mac)
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    ]
    
    BASE_URL = "https://new.land.naver.com"
    
    def __init__(self):
        """크롤러 초기화"""
        self.session = requests.Session()
        self._update_headers()
        self._visit_homepage()  # 초기 방문으로 쿠키 받기
    
    def _visit_homepage(self):
        """
        네이버 부동산 홈페이지 방문 (쿠키 받기)
        실제 브라우저처럼 동작하기 위해
        """
        try:
            logger.info("네이버 부동산 홈페이지 방문 중...")
            self.session.get(self.BASE_URL, timeout=10)
            time.sleep(random.uniform(2, 4))
            logger.info("초기 방문 완료")
        except Exception as e:
            logger.warning(f"초기 방문 실패: {e}")
    
    def _update_headers(self):
        """요청 헤더 업데이트 (차단 회피)"""
        self.session.headers.update({
            'User-Agent': random.choice(self.USER_AGENTS),
            'Referer': 'https://new.land.naver.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def _safe_request(self, url: str, params: Dict = None, retry: int = 3) -> Optional[Dict]:
        """
        안전한 HTTP 요청 (재시도 포함, 429 에러 특별 처리)
        
        Args:
            url: 요청 URL
            params: 쿼리 파라미터
            retry: 재시도 횟수
            
        Returns:
            JSON 응답 또는 None
        """
        for attempt in range(retry):
            try:
                # 기본 요청 전 딜레이 (속도 제한)
                if attempt == 0:
                    time.sleep(random.uniform(1, 2))
                
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                
                elif response.status_code == 429:
                    # 429 Too Many Requests - 특별 처리!
                    # 지수 백오프: 시도마다 대기 시간 증가
                    wait_time = random.uniform(30, 60) * (2 ** attempt)  # 30초 → 60초 → 120초
                    logger.warning(f"⚠️  429 에러 (Too Many Requests)")
                    logger.info(f"📢 권장 대기 시간: {wait_time:.1f}초 대기...")
                    
                    if attempt < retry - 1:
                        logger.info(f"재시도 예정 ({attempt + 2}/{retry})")
                        time.sleep(wait_time)
                        self._update_headers()  # User-Agent 변경
                    else:
                        logger.error("❌ 최대 재시도 횟수 초과. 나중에 다시 시도하세요.")
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
            
            # 랜덤 딜레이 (차단 회피) - 더 길게!
            time.sleep(random.uniform(3, 6))
            
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
        
        # 랜덤 딜레이 - 더 길게!
        time.sleep(random.uniform(2, 4))
        
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
        
        for trade_type in trade_types:
            logger.info(f"=== 거래 유형 {trade_type} 크롤링 시작 ===")
            
            # 1. 단지 목록 가져오기
            complexes = self.search_complexes(cortarNo, trade_type)
            
            # 2. 각 단지의 매물 가져오기
            for i, complex_info in enumerate(complexes[:10], 1):  # 테스트: 상위 10개만
                complex_no = complex_info.get('complexNo')
                complex_name = complex_info.get('complexName', '알 수 없음')
                
                logger.info(f"[{i}/{len(complexes[:10])}] {complex_name} (complexNo: {complex_no})")
                
                articles = self.get_complex_articles(complex_no, trade_type)
                
                for article in articles:
                    # 매물 데이터 가공
                    property_data = self._parse_article(article, complex_info, trade_type)
                    all_properties.append(property_data)
                
                # 단지 간 딜레이 - 더 길게! (차단 방지)
                delay = random.uniform(5, 10)
                logger.info(f"다음 단지 크롤링 전 {delay:.1f}초 대기...")
                time.sleep(delay)
        
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
