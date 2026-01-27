"""
네이버 부동산 크롤러 V2
Playwright 완전 자동화 버전 (모바일)
"""

import logging
import time
import random
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)


class NaverRealEstateScraperV2:
    """네이버 부동산 크롤러 V2 - 완전한 브라우저 자동화"""
    
    def __init__(self):
        """크롤러 초기화"""
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    def start(self):
        """브라우저 시작"""
        logger.info("브라우저 시작 중...")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False,  # 디버깅용
            args=['--disable-blink-features=AutomationControlled']
        )
        self.context = self.browser.new_context(
            viewport={'width': 375, 'height': 667},  # 모바일 사이즈
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            locale='ko-KR'
        )
        self.page = self.context.new_page()
        
        logger.info("브라우저 시작 완료!")
    
    def stop(self):
        """브라우저 종료"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        
        logger.info("브라우저 종료 완료!")
    
    def search_region(self, region_name: str, trade_type: str = "B1") -> List[Dict]:
        """
        지역 검색 및 매물 목록 가져오기
        
        Args:
            region_name: 지역명 (예: "강남구 대치동")
            trade_type: 거래 유형 (A1: 매매, B1: 전세, B2: 월세)
            
        Returns:
            매물 목록
        """
        try:
            # 1. 모바일 메인 페이지 방문
            logger.info(f"지역 검색: {region_name}")
            url = f"https://m.land.naver.com/search/result/{region_name}"
            
            self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 2. 페이지 로딩 대기
            time.sleep(3)
            
            # 3. 지도 버튼 클릭 (지도 뷰로 전환)
            try:
                self.page.click('button:has-text("지도")', timeout=5000)
                time.sleep(2)
            except:
                logger.warning("지도 버튼을 찾을 수 없습니다.")
            
            # 4. 매물 목록 추출
            properties = self.page.evaluate("""
                () => {
                    const items = document.querySelectorAll('[class*="item"]');
                    return Array.from(items).slice(0, 10).map(item => {
                        const title = item.querySelector('[class*="title"]')?.textContent?.trim();
                        const price = item.querySelector('[class*="price"]')?.textContent?.trim();
                        const info = item.querySelector('[class*="info"]')?.textContent?.trim();
                        
                        return {
                            title: title || '알 수 없음',
                            price: price || '가격 정보 없음',
                            info: info || '상세 정보 없음'
                        };
                    }).filter(item => item.title !== '알 수 없음');
                }
            """)
            
            logger.info(f"추출된 매물 수: {len(properties)}개")
            
            # 스크린샷 저장 (디버깅용)
            self.page.screenshot(path='search_result.png')
            logger.info("스크린샷 저장: search_result.png")
            
            return properties
            
        except Exception as e:
            logger.error(f"지역 검색 실패: {e}")
            return []
    
    def get_property_details(self, property_url: str) -> Dict:
        """
        매물 상세 정보 가져오기
        
        Args:
            property_url: 매물 URL
            
        Returns:
            매물 상세 정보
        """
        try:
            self.page.goto(property_url, wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            # 상세 정보 추출
            details = self.page.evaluate("""
                () => {
                    return {
                        title: document.querySelector('[class*="title"]')?.textContent?.trim() || '',
                        price: document.querySelector('[class*="price"]')?.textContent?.trim() || '',
                        area: document.querySelector('[class*="area"]')?.textContent?.trim() || '',
                        floor: document.querySelector('[class*="floor"]')?.textContent?.trim() || ''
                    };
                }
            """)
            
            return details
            
        except Exception as e:
            logger.error(f"상세 정보 가져오기 실패: {e}")
            return {}


# 테스트 코드
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    import json
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # ✅ .env 파일에서 설정 읽기
    load_dotenv()
    
    search_regions = os.getenv('SEARCH_REGIONS', '').split(',')
    trade_types = os.getenv('TRADE_TYPES', 'B1,B2').split(',')
    
    # ✅ config/filters.json 읽기
    try:
        with open('config/filters.json', 'r', encoding='utf-8') as f:
            filters = json.load(f)
        
        print("=" * 80)
        print("필터 설정 확인:")
        print(f"  - 검색 지역 코드: {search_regions}")
        print(f"  - 거래 유형: {trade_types}")
        print(f"  - 매물 유형: {filters.get('property_types', [])}")
        print(f"  - 전세 가격: {filters['price_range']['B1']['min']:,}~{filters['price_range']['B1']['max']:,}만원")
        print(f"  - 월세 가격: {filters['price_range']['B2']['min']}~{filters['price_range']['B2']['max']}만원")
        print(f"  - 면적: {filters['area_range']['min']}~{filters['area_range']['max']}m²")
        print(f"  - 방 개수: {filters.get('room_count', [])}")
        print("=" * 80)
        
    except Exception as e:
        print(f"⚠️ 필터 파일 읽기 실패: {e}")
        filters = {}
    
    scraper = NaverRealEstateScraperV2()
    
    try:
        scraper.start()
        
        # ✅ 사용자 설정 지역으로 검색
        for region_code in search_regions:
            if not region_code.strip():
                continue
            
            print(f"\n{'='*80}")
            print(f"지역 코드 {region_code} 검색 중...")
            print(f"{'='*80}")
            
            # 지역 코드로 검색 (모바일 버전은 코드 대신 이름 필요)
            # 일단 테스트용으로 실행
            properties = scraper.search_region(f"region_{region_code}")
            
            print(f"\n검색 결과: {len(properties)}개 매물")
            for i, prop in enumerate(properties, 1):
                print(f"\n{i}. {prop['title']}")
                print(f"   가격: {prop['price']}")
                print(f"   정보: {prop['info']}")
        
        # 30초 대기 (브라우저 확인)
        print("\n30초 대기 중...")
        time.sleep(30)
        
    finally:
        scraper.stop()
