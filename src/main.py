"""
네이버 부동산 크롤링 텔레그램 봇 메인 실행 파일
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

# 로컬 모듈 임포트
from database import PropertyDatabase
from scraper import NaverRealEstateScraper
from filter_manager import FilterManager
from telegram_bot import TelegramNotifierSync

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('scraper.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class RealEstateBot:
    """부동산 크롤링 봇 메인 클래스"""
    
    def __init__(self):
        """봇 초기화"""
        # 환경 변수 로드
        load_dotenv()
        
        # 설정 로드
        self.search_regions = os.getenv('SEARCH_REGIONS', '').split(',')
        self.trade_types = os.getenv('TRADE_TYPES', 'A1,B1').split(',')
        
        # 모듈 초기화
        self.db = PropertyDatabase('data/properties.db')
        self.scraper = NaverRealEstateScraper()
        self.filter_manager = FilterManager('config/filters.json')
        
        # 텔레그램 봇 초기화 (선택적)
        try:
            self.telegram = TelegramNotifierSync()
            self.use_telegram = True
            logger.info("텔레그램 봇 초기화 완료")
        except ValueError as e:
            logger.warning(f"텔레그램 봇 초기화 실패: {e}")
            self.use_telegram = False
        
        logger.info("RealEstateBot 초기화 완료")
    
    def run(self):
        """메인 실행 로직"""
        try:
            logger.info("=" * 60)
            logger.info("부동산 크롤링 시작")
            logger.info(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)
            
            # 통계 초기화
            total_crawled = 0
            new_properties = 0
            filtered_properties = 0
            notified_properties = 0
            
            # 각 지역별로 크롤링
            for region in self.search_regions:
                if not region.strip():
                    continue
                
                logger.info(f"\n[지역 크롤링] cortarNo: {region}")
                
                # 1. 매물 크롤링
                properties = self.scraper.scrape_region(
                    cortarNo=region.strip(),
                    trade_types=self.trade_types
                )
                total_crawled += len(properties)
                logger.info(f"크롤링 완료: {len(properties)}개 매물")
                
                # 2. 필터 적용
                filtered = self.filter_manager.filter_properties(properties)
                filtered_properties += len(filtered)
                logger.info(f"필터 통과: {len(filtered)}개 매물")
                
                # 3. 신규 매물 확인 및 저장
                for prop in filtered:
                    if self.db.add_property(prop):
                        new_properties += 1
                        logger.info(f"신규 매물 발견: {prop['complex_name']} - {prop['id']}")
                        
                        # 4. 텔레그램 알림 전송
                        if self.use_telegram:
                            try:
                                success = self.telegram.send_property_notification(prop)
                                if success:
                                    notified_properties += 1
                                    self.db.mark_as_notified(prop['id'])
                                    logger.info("알림 전송 완료")
                            except Exception as e:
                                logger.error(f"알림 전송 실패: {e}")
            
            # 5. 결과 요약
            logger.info("\n" + "=" * 60)
            logger.info("크롤링 완료 요약")
            logger.info("=" * 60)
            logger.info(f"전체 크롤링 매물: {total_crawled}개")
            logger.info(f"필터 통과 매물: {filtered_properties}개")
            logger.info(f"신규 매물: {new_properties}개")
            logger.info(f"알림 전송: {notified_properties}개")
            
            # 데이터베이스 통계
            db_stats = self.db.get_stats()
            logger.info(f"\n[데이터베이스 통계]")
            logger.info(f"총 저장 매물: {db_stats['total']}개")
            logger.info(f"알림 완료: {db_stats['notified']}개")
            logger.info(f"알림 대기: {db_stats['pending']}개")
            
            # 텔레그램 요약 메시지 전송
            if self.use_telegram and new_properties > 0:
                try:
                    summary_msg = f"""📊 크롤링 완료 보고

🔍 전체 매물: {total_crawled}개
✅ 필터 통과: {filtered_properties}개
✨ 신규 매물: {new_properties}개
📬 알림 전송: {notified_properties}개

💾 DB 총 매물: {db_stats['total']}개
⏰ 다음 실행: 2시간 후
"""
                    self.telegram.send_message(summary_msg)
                except Exception as e:
                    logger.error(f"요약 메시지 전송 실패: {e}")
            
            logger.info("\n" + "=" * 60)
            logger.info("모든 작업 완료")
            logger.info("=" * 60)
            
            return {
                'success': True,
                'total_crawled': total_crawled,
                'new_properties': new_properties,
                'filtered_properties': filtered_properties,
                'notified_properties': notified_properties
            }
            
        except Exception as e:
            logger.error(f"실행 중 오류 발생: {e}", exc_info=True)
            
            # 에러 알림 전송
            if self.use_telegram:
                try:
                    error_msg = f"⚠️ 오류 발생\n\n{str(e)}\n\n잠시 후 다시 시도됩니다."
                    self.telegram.send_message(error_msg)
                except:
                    pass
            
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """메인 함수"""
    try:
        bot = RealEstateBot()
        result = bot.run()
        
        if result['success']:
            logger.info("프로그램 정상 종료")
            sys.exit(0)
        else:
            logger.error(f"프로그램 오류 종료: {result.get('error', '알 수 없는 오류')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
        sys.exit(0)
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
