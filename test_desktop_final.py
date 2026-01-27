"""
데스크톱 버전 네이버 부동산 테스트
사용자 설정 파일 기반
"""

import os
import json
import time
import logging
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_desktop():
    """데스크톱 버전 테스트"""
    
    # 설정 로드
    load_dotenv()
    
    search_regions = os.getenv('SEARCH_REGIONS', '').split(',')
    trade_types = os.getenv('TRADE_TYPES', 'B1,B2').split(',')
    
    # 필터 로드
    try:
        with open('config/filters.json', 'r', encoding='utf-8') as f:
            filters = json.load(f)
        
        logger.info("=" * 80)
        logger.info("필터 설정:")
        logger.info(f"  - 지역 코드: {search_regions}")
        logger.info(f"  - 거래 유형: {trade_types}")
        logger.info(f"  - 전세 가격: {filters['price_range']['B1']['min']:,}~{filters['price_range']['B1']['max']:,}만원")
        logger.info(f"  - 면적: {filters['area_range']['min']}~{filters['area_range']['max']}m²")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"필터 파일 읽기 실패: {e}")
        return
    
    with sync_playwright() as p:
        # 브라우저 시작
        logger.info("브라우저 시작...")
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='ko-KR'
        )
        
        page = context.new_page()
        
        try:
            # 각 지역에 대해 검색
            for region_code in search_regions:
                if not region_code.strip():
                    continue
                
                for trade_type in trade_types:
                    logger.info("=" * 80)
                    logger.info(f"검색: 지역코드={region_code}, 거래유형={trade_type}")
                    logger.info("=" * 80)
                    
                    # URL 구성
                    url = f"https://new.land.naver.com/complexes?cortarNo={region_code}&tradeType={trade_type}"
                    logger.info(f"URL: {url}")
                    
                    # 페이지 방문
                    page.goto(url, wait_until='networkidle', timeout=30000)
                    logger.info("페이지 로딩 완료")
                    
                    # 충분한 대기 시간
                    time.sleep(5)
                    
                    # 페이지 제목 확인
                    title = page.title()
                    logger.info(f"페이지 제목: {title}")
                    
                    # 스크린샷 저장
                    screenshot_path = f'desktop_result_{region_code}_{trade_type}.png'
                    page.screenshot(path=screenshot_path, full_page=True)
                    logger.info(f"스크린샷 저장: {screenshot_path}")
                    
                    # HTML 저장
                    html = page.content()
                    html_path = f'desktop_page_{region_code}_{trade_type}.html'
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html)
                    logger.info(f"HTML 저장: {html_path}")
                    
                    # JavaScript로 데이터 추출 시도
                    logger.info("데이터 추출 시도 중...")
                    
                    data = page.evaluate("""
                        () => {
                            // 모든 링크 찾기
                            const links = Array.from(document.querySelectorAll('a')).slice(0, 5);
                            const linkTexts = links.map(a => a.textContent.trim());
                            
                            // 페이지에 'complex'가 포함된 요소 찾기
                            const complexElements = Array.from(document.querySelectorAll('[class*="complex"]'));
                            
                            // 페이지의 모든 텍스트
                            const bodyText = document.body.innerText.substring(0, 500);
                            
                            return {
                                linkCount: links.length,
                                linkTexts: linkTexts,
                                complexElementCount: complexElements.length,
                                bodyTextPreview: bodyText
                            };
                        }
                    """)
                    
                    logger.info(f"링크 수: {data['linkCount']}")
                    logger.info(f"링크 텍스트: {data['linkTexts']}")
                    logger.info(f"Complex 요소 수: {data['complexElementCount']}")
                    logger.info(f"페이지 텍스트 미리보기: {data['bodyTextPreview'][:200]}")
                    
                    # 30초 대기 (브라우저 확인용)
                    logger.info("\n30초 대기 중... (브라우저를 직접 확인하세요)")
                    time.sleep(30)
            
        finally:
            browser.close()
            logger.info("브라우저 종료 완료")

if __name__ == "__main__":
    test_desktop()
