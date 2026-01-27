"""
텔레그램 봇 메시지 전송 모듈
"""

import os
from typing import List, Dict
import logging
from telegram import Bot
from telegram.error import TelegramError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """텔레그램 알림 클래스"""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        """
        텔레그램 알림 초기화
        
        Args:
            bot_token: 봇 토큰 (없으면 환경 변수에서 가져옴)
            chat_id: 채팅 ID (없으면 환경 변수에서 가져옴)
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token or not self.chat_id:
            raise ValueError("텔레그램 봇 토큰과 채팅 ID가 필요합니다.")
        
        self.bot = Bot(token=self.bot_token)
        logger.info("텔레그램 봇 초기화 완료")
    
    def format_property_message(self, property_data: Dict) -> str:
        """
        매물 정보를 텔레그램 메시지 형식으로 변환
        
        Args:
            property_data: 매물 정보
            
        Returns:
            포맷된 메시지
        """
        # 거래 유형 변환
        trade_type_map = {
            'A1': '매매',
            'B1': '전세',
            'B2': '월세',
            'B3': '단기임대'
        }
        trade_type = trade_type_map.get(property_data.get('trade_type', ''), '알 수 없음')
        
        # 가격 포맷 (만원 단위)
        price = property_data.get('price', 0)
        if price >= 10000:
            price_str = f"{price // 10000}억 {price % 10000}만원" if price % 10000 else f"{price // 10000}억원"
        else:
            price_str = f"{price}만원"
        
        # 면적 포맷
        area_real = property_data.get('area_real', 0)
        area_exclusive = property_data.get('area_exclusive', 0)
        area_str = f"{area_real:.1f}㎡ (전용 {area_exclusive:.1f}㎡)"
        
        # 층수 정보
        floor = property_data.get('floor', '정보 없음')
        total_floors = property_data.get('total_floors', 0)
        floor_str = f"{floor}" if '/' in floor else f"{floor}/{total_floors}층"
        
        # 방향
        direction = property_data.get('direction', '정보 없음')
        
        # 승인연도
        approval_year = property_data.get('approval_year', 0)
        if approval_year:
            current_year = 2026  # 현재 연도
            building_age = current_year - int(approval_year)
            approval_str = f"{approval_year}년 ({building_age}년차)"
        else:
            approval_str = "정보 없음"
        
        # 세대수
        household_count = property_data.get('household_count', 0)
        
        # 방/욕실
        room_count = property_data.get('room_count', 0)
        bathroom_count = property_data.get('bathroom_count', 0)
        room_info = f"방 {room_count}개, 욕실 {bathroom_count}개" if room_count or bathroom_count else ""
        
        # URL
        url = property_data.get('url', '')
        
        # 메시지 조합
        message = f"""🏠 **새 매물 발견!**

📌 **단지명**: {property_data.get('complex_name', '정보 없음')}
💰 **거래**: {trade_type} {price_str}
📐 **면적**: {area_str}
🏢 **층수**: {floor_str}
🧭 **방향**: {direction}
📅 **승인**: {approval_str}
🏘 **세대수**: {household_count}세대"""

        if room_info:
            message += f"\n🛏 **구조**: {room_info}"
        
        message += f"\n\n🔗 [상세보기]({url})"
        
        return message
    
    async def send_message(self, message: str) -> bool:
        """
        메시지 전송
        
        Args:
            message: 전송할 메시지
            
        Returns:
            전송 성공 여부
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
            logger.info("메시지 전송 완료")
            return True
            
        except TelegramError as e:
            logger.error(f"텔레그램 전송 오류: {e}")
            return False
    
    async def send_property_notification(self, property_data: Dict) -> bool:
        """
        매물 알림 전송
        
        Args:
            property_data: 매물 정보
            
        Returns:
            전송 성공 여부
        """
        message = self.format_property_message(property_data)
        return await self.send_message(message)
    
    async def send_summary(self, total_properties: int, new_properties: int, filtered_properties: int) -> bool:
        """
        실행 결과 요약 전송
        
        Args:
            total_properties: 전체 크롤링 매물 수
            new_properties: 신규 매물 수
            filtered_properties: 필터 통과 매물 수
            
        Returns:
            전송 성공 여부
        """
        message = f"""📊 **크롤링 완료 보고**

🔍 **전체 매물**: {total_properties}개
✨ **신규 매물**: {new_properties}개
✅ **필터 통과**: {filtered_properties}개
📬 **알림 전송**: {filtered_properties}개

⏰ 다음 실행: 2시간 후
"""
        return await self.send_message(message)
    
    async def send_error(self, error_message: str) -> bool:
        """
        에러 메시지 전송
        
        Args:
            error_message: 에러 내용
            
        Returns:
            전송 성공 여부
        """
        message = f"""⚠️ **오류 발생**

{error_message}

잠시 후 다시 시도됩니다.
"""
        return await self.send_message(message)


# 동기 버전 래퍼 (GitHub Actions에서 사용)
class TelegramNotifierSync:
    """동기 방식 텔레그램 알림 클래스"""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token or not self.chat_id:
            raise ValueError("텔레그램 봇 토큰과 채팅 ID가 필요합니다.")
        
        logger.info("텔레그램 봇 초기화 완료 (동기)")
    
    def format_property_message(self, property_data: Dict) -> str:
        """매물 정보를 메시지로 변환"""
        # 위와 동일한 로직
        trade_type_map = {'A1': '매매', 'B1': '전세', 'B2': '월세', 'B3': '단기임대'}
        trade_type = trade_type_map.get(property_data.get('trade_type', ''), '알 수 없음')
        
        price = property_data.get('price', 0)
        if price >= 10000:
            price_str = f"{price // 10000}억 {price % 10000}만원" if price % 10000 else f"{price // 10000}억원"
        else:
            price_str = f"{price}만원"
        
        area_real = property_data.get('area_real', 0)
        area_exclusive = property_data.get('area_exclusive', 0)
        
        message = f"""🏠 새 매물 발견!

📌 단지명: {property_data.get('complex_name', '정보 없음')}
💰 거래: {trade_type} {price_str}
📐 면적: {area_real:.1f}㎡ (전용 {area_exclusive:.1f}㎡)
🏢 층수: {property_data.get('floor', '정보 없음')}
🧭 방향: {property_data.get('direction', '정보 없음')}

🔗 {property_data.get('url', '')}
"""
        return message
    
    def send_message(self, message: str) -> bool:
        """메시지 전송 (requests 사용)"""
        import requests
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("메시지 전송 완료")
                return True
            else:
                logger.error(f"메시지 전송 실패: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"메시지 전송 오류: {e}")
            return False
    
    def send_property_notification(self, property_data: Dict) -> bool:
        """매물 알림 전송"""
        message = self.format_property_message(property_data)
        return self.send_message(message)


if __name__ == "__main__":
    # 테스트 코드
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # 테스트 매물
    test_property = {
        'complex_name': '래미안 강남파크팰리스',
        'trade_type': 'A1',
        'price': 135000,
        'area_real': 84.5,
        'area_exclusive': 59.2,
        'floor': '15/25',
        'direction': '남향',
        'approval_year': 2020,
        'household_count': 850,
        'room_count': 3,
        'bathroom_count': 2,
        'url': 'https://new.land.naver.com/complexes/12345?articleNo=67890'
    }
    
    # 동기 버전 테스트
    try:
        notifier = TelegramNotifierSync()
        notifier.send_property_notification(test_property)
        print("테스트 메시지 전송 완료")
    except Exception as e:
        print(f"테스트 실패: {e}")
