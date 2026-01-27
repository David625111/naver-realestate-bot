"""
필터 설정 관리 및 매물 필터링 모듈
"""

import json
import os
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FilterManager:
    """필터 관리 클래스"""
    
    def __init__(self, config_path: str = "config/filters.json"):
        """
        필터 관리자 초기화
        
        Args:
            config_path: 필터 설정 파일 경로
        """
        self.config_path = config_path
        self.filters = self._load_filters()
    
    def _load_filters(self) -> Dict:
        """필터 설정 로드"""
        if not os.path.exists(self.config_path):
            logger.warning(f"필터 설정 파일이 없습니다: {self.config_path}")
            return self._get_default_filters()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                filters = json.load(f)
                logger.info("필터 설정 로드 완료")
                return filters
        except Exception as e:
            logger.error(f"필터 설정 로드 실패: {e}")
            return self._get_default_filters()
    
    def _get_default_filters(self) -> Dict:
        """기본 필터 설정 반환"""
        return {
            "property_types": ["APT", "OPST"],
            "trade_types": ["A1", "B1"],
            "price_range": {
                "A1": {"min": 0, "max": 999999},
                "B1": {"min": 0, "max": 999999}
            },
            "area_range": {"min": 0, "max": 999999},
            "approval_year": {"min": 0, "max": 9999},
            "household_count": {"min": 0, "max": 999999},
            "floor_types": [],
            "room_count": [],
            "bathroom_count": [],
            "directions": [],
            "loan": "상관없음",
            "options": []
        }
    
    def apply_filters(self, property_data: Dict) -> bool:
        """
        매물에 필터 적용
        
        Args:
            property_data: 매물 정보
            
        Returns:
            필터 통과 여부
        """
        try:
            # 1. 거래 유형 필터
            trade_type = property_data.get('trade_type', '')
            if trade_type not in self.filters.get('trade_types', []):
                logger.debug(f"거래 유형 불일치: {trade_type}")
                return False
            
            # 2. 가격 필터
            price = property_data.get('price', 0)
            price_filter = self.filters.get('price_range', {}).get(trade_type, {})
            if price < price_filter.get('min', 0) or price > price_filter.get('max', 999999):
                logger.debug(f"가격 범위 초과: {price}")
                return False
            
            # 3. 면적 필터
            area = property_data.get('area_exclusive', 0)
            area_filter = self.filters.get('area_range', {})
            if area < area_filter.get('min', 0) or area > area_filter.get('max', 999999):
                logger.debug(f"면적 범위 초과: {area}")
                return False
            
            # 4. 사용승인연도 필터
            approval_year = int(property_data.get('approval_year', 0))
            year_filter = self.filters.get('approval_year', {})
            if approval_year < year_filter.get('min', 0) or approval_year > year_filter.get('max', 9999):
                logger.debug(f"승인연도 범위 초과: {approval_year}")
                return False
            
            # 5. 세대수 필터
            household_count = property_data.get('household_count', 0)
            household_filter = self.filters.get('household_count', {})
            if household_count < household_filter.get('min', 0) or household_count > household_filter.get('max', 999999):
                logger.debug(f"세대수 범위 초과: {household_count}")
                return False
            
            # 6. 층수 필터
            floor_types = self.filters.get('floor_types', [])
            if floor_types and len(floor_types) > 0:
                floor_info = property_data.get('floor', '')
                floor_match = self._check_floor_type(floor_info, floor_types)
                if not floor_match:
                    logger.debug(f"층수 조건 불일치: {floor_info}")
                    return False
            
            # 7. 방 개수 필터
            room_counts = self.filters.get('room_count', [])
            if room_counts and len(room_counts) > 0:
                room_count = property_data.get('room_count', 0)
                if room_count not in room_counts:
                    logger.debug(f"방 개수 불일치: {room_count}")
                    return False
            
            # 8. 욕실 개수 필터
            bathroom_counts = self.filters.get('bathroom_count', [])
            if bathroom_counts and len(bathroom_counts) > 0:
                bathroom_count = property_data.get('bathroom_count', 0)
                if bathroom_count not in bathroom_counts:
                    logger.debug(f"욕실 개수 불일치: {bathroom_count}")
                    return False
            
            # 9. 방향 필터
            directions = self.filters.get('directions', [])
            if directions and len(directions) > 0:
                direction = property_data.get('direction', '')
                if direction not in directions:
                    logger.debug(f"방향 불일치: {direction}")
                    return False
            
            # 10. 융자금 필터
            loan_filter = self.filters.get('loan', '상관없음')
            if loan_filter != '상관없음':
                loan_amount = property_data.get('loan_amount', 0)
                if loan_filter == '융자금 없음' and loan_amount > 0:
                    logger.debug(f"융자금 있음: {loan_amount}")
                    return False
                elif loan_filter == '융자금30%미만':
                    price = property_data.get('price', 1)
                    if price > 0 and (loan_amount / price) >= 0.3:
                        logger.debug(f"융자금 30% 이상: {loan_amount}/{price}")
                        return False
            
            logger.info(f"필터 통과: {property_data.get('complex_name', '')} - {property_data.get('id', '')}")
            return True
            
        except Exception as e:
            logger.error(f"필터 적용 중 오류: {e}")
            return False
    
    def _check_floor_type(self, floor_info: str, floor_types: List[str]) -> bool:
        """
        층수 타입 확인
        
        Args:
            floor_info: 층 정보 (예: "5/25")
            floor_types: 필터할 층 타입 리스트
            
        Returns:
            조건 일치 여부
        """
        try:
            if '/' not in floor_info:
                return False
            
            current_floor, total_floor = floor_info.split('/')
            current_floor = int(current_floor)
            total_floor = int(total_floor)
            
            for floor_type in floor_types:
                if floor_type == "1층" and current_floor == 1:
                    return True
                elif floor_type == "저층" and 2 <= current_floor <= total_floor // 3:
                    return True
                elif floor_type == "중간층" and total_floor // 3 < current_floor <= (total_floor * 2) // 3:
                    return True
                elif floor_type == "고층" and (total_floor * 2) // 3 < current_floor < total_floor:
                    return True
                elif floor_type == "탑층" and current_floor == total_floor:
                    return True
            
            return False
            
        except:
            return False
    
    def filter_properties(self, properties: List[Dict]) -> List[Dict]:
        """
        매물 리스트에 필터 적용
        
        Args:
            properties: 매물 리스트
            
        Returns:
            필터링된 매물 리스트
        """
        filtered = []
        
        for prop in properties:
            if self.apply_filters(prop):
                filtered.append(prop)
        
        logger.info(f"필터링 결과: {len(properties)}개 중 {len(filtered)}개 통과")
        return filtered


if __name__ == "__main__":
    # 테스트 코드
    filter_mgr = FilterManager("../config/filters.json")
    
    # 테스트 매물
    test_property = {
        'id': 'test_001',
        'complex_name': '테스트아파트',
        'trade_type': 'A1',
        'price': 100000,
        'area_exclusive': 70,
        'approval_year': 2020,
        'household_count': 500,
        'floor': '10/25',
        'room_count': 3,
        'bathroom_count': 2,
        'direction': '남향',
        'loan_amount': 0
    }
    
    result = filter_mgr.apply_filters(test_property)
    print(f"필터 테스트 결과: {'통과' if result else '실패'}")
