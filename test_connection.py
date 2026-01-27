"""
네이버 부동산 연결 테스트
쿠키 수신 및 헤더 설정 확인
"""

import sys
sys.path.insert(0, 'src')

from scraper import NaverRealEstateScraper
import logging

# 로깅 레벨 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_connection():
    """네이버 부동산 연결 테스트"""
    logger.info("=" * 60)
    logger.info("네이버 부동산 연결 테스트 시작")
    logger.info("=" * 60)
    
    # 크롤러 생성 (초기화 과정에서 메인 페이지 방문 및 쿠키 수신)
    scraper = NaverRealEstateScraper()
    
    # 쿠키 확인
    cookies = scraper.session.cookies.get_dict()
    logger.info(f"\n📊 테스트 결과:")
    logger.info(f"   쿠키 수신 여부: {'✅ 성공' if scraper.cookies_received else '❌ 실패'}")
    logger.info(f"   수신된 쿠키 수: {len(cookies)}개")
    
    if cookies:
        logger.info(f"   쿠키 목록:")
        for key in cookies.keys():
            logger.info(f"      - {key}")
    
    # 브라우저 프로파일 확인
    if scraper.current_browser_profile:
        browser_type = scraper.current_browser_profile['type']
        logger.info(f"\n   브라우저 타입: {browser_type.upper()}")
        logger.info(f"   User-Agent: {scraper.current_browser_profile['user_agent'][:80]}...")
    
    logger.info("\n" + "=" * 60)
    logger.info("연결 테스트 완료!")
    logger.info("=" * 60)
    
    return scraper.cookies_received

if __name__ == "__main__":
    success = test_connection()
    
    if success:
        print("\n✅ 연결 테스트 성공! 크롤링을 시작할 수 있습니다.")
    else:
        print("\n❌ 연결 테스트 실패. 쿠키를 받지 못했습니다.")
