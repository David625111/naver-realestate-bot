"""
최소한의 크롤링 테스트
단지 1개만 크롤링하여 작동 여부 확인
"""

import sys
sys.path.insert(0, 'src')

from scraper import NaverRealEstateScraper
import logging

# 로깅 레벨 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_minimal_crawl():
    """최소한의 크롤링 테스트 (단지 1개)"""
    logger.info("=" * 80)
    logger.info("✅ Playwright 버전 크롤링 테스트 시작!")
    logger.info("실제 Chromium 브라우저를 사용하여 쿠키를 획득합니다.")
    logger.info("주의: 2배 빠른 속도 (0.5-30분 대기)")
    logger.info("=" * 80)
    
    # 크롤러 생성 (Playwright 사용!)
    scraper = NaverRealEstateScraper(use_browser=True)
    
    # 강남구 대치동 지역 코드
    cortarNo = "1168010600"
    
    try:
        # 단지 검색
        logger.info(f"\n[1/3] 단지 검색 중... (cortarNo: {cortarNo})")
        complexes = scraper.search_complexes(cortarNo, trade_type="B1")  # 전세
        
        if not complexes:
            logger.error("단지를 찾지 못했습니다. 429 에러 또는 차단되었을 가능성 있음.")
            return False
        
        logger.info(f"✅ 검색된 단지 수: {len(complexes)}개")
        
        # 첫 번째 단지만 테스트
        if complexes:
            complex_info = complexes[0]
            complex_no = complex_info.get('complexNo')
            complex_name = complex_info.get('complexName', '알 수 없음')
            
            logger.info(f"\n[2/3] 매물 목록 가져오기... ({complex_name})")
            articles = scraper.get_complex_articles(complex_no, trade_type="B1")
            
            if articles:
                logger.info(f"✅ 검색된 매물 수: {len(articles)}개")
                logger.info(f"\n[3/3] 첫 번째 매물 정보:")
                article = articles[0]
                
                # 매물 정보 파싱
                property_data = scraper._parse_article(article, complex_info, "B1")
                
                logger.info(f"   단지명: {property_data['complex_name']}")
                logger.info(f"   가격: {property_data['price']:,}만원")
                logger.info(f"   면적: {property_data['area_exclusive']}m²")
                logger.info(f"   층: {property_data['floor']}")
                logger.info(f"   URL: {property_data['url']}")
                
                logger.info("\n" + "=" * 80)
                logger.info("✅ 테스트 성공! 크롤링이 정상 작동합니다!")
                logger.info("=" * 80)
                return True
            else:
                logger.error("매물을 찾지 못했습니다.")
                return False
        
    except Exception as e:
        logger.error(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_minimal_crawl()
        
        if success:
            print("\n" + "=" * 80)
            print("✅ 테스트 성공! Selenium + requests 하이브리드 방식이 작동합니다!")
            print("=" * 80)
        else:
            print("\n" + "=" * 80)
            print("❌ 테스트 실패. 로그를 확인하세요.")
            print("=" * 80)
    
    except KeyboardInterrupt:
        print("\n\n테스트 중단됨.")
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
