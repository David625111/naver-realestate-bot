"""
SQLite 데이터베이스 관리 모듈
매물 데이터 저장 및 중복 확인
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional


class PropertyDatabase:
    """부동산 매물 데이터베이스 관리 클래스"""
    
    def __init__(self, db_path: str = "data/properties.db"):
        """
        데이터베이스 초기화
        
        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = db_path
        
        # 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 데이터베이스 연결 및 테이블 생성
        self._init_database()
    
    def _init_database(self):
        """데이터베이스 테이블 생성"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS properties (
                    id TEXT PRIMARY KEY,
                    complex_no TEXT,
                    complex_name TEXT,
                    article_no TEXT,
                    price INTEGER,
                    area_real REAL,
                    area_exclusive REAL,
                    floor TEXT,
                    total_floors INTEGER,
                    direction TEXT,
                    trade_type TEXT,
                    approval_year INTEGER,
                    household_count INTEGER,
                    room_count INTEGER,
                    bathroom_count INTEGER,
                    loan_amount INTEGER,
                    description TEXT,
                    url TEXT,
                    first_seen TIMESTAMP,
                    last_checked TIMESTAMP,
                    notified BOOLEAN DEFAULT 0
                )
            """)
            
            # 인덱스 생성 (빠른 검색을 위해)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_complex_no 
                ON properties(complex_no)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notified 
                ON properties(notified)
            """)
            
            conn.commit()
    
    def property_exists(self, property_id: str) -> bool:
        """
        매물이 이미 데이터베이스에 존재하는지 확인
        
        Args:
            property_id: 매물 고유 ID
            
        Returns:
            존재 여부
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM properties WHERE id = ?",
                (property_id,)
            )
            count = cursor.fetchone()[0]
            return count > 0
    
    def add_property(self, property_data: Dict) -> bool:
        """
        새 매물 추가
        
        Args:
            property_data: 매물 정보 딕셔너리
            
        Returns:
            추가 성공 여부
        """
        if self.property_exists(property_data['id']):
            return False
        
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO properties (
                    id, complex_no, complex_name, article_no,
                    price, area_real, area_exclusive, floor, total_floors,
                    direction, trade_type, approval_year, household_count,
                    room_count, bathroom_count, loan_amount, description,
                    url, first_seen, last_checked, notified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                property_data['id'],
                property_data.get('complex_no', ''),
                property_data.get('complex_name', ''),
                property_data.get('article_no', ''),
                property_data.get('price', 0),
                property_data.get('area_real', 0),
                property_data.get('area_exclusive', 0),
                property_data.get('floor', ''),
                property_data.get('total_floors', 0),
                property_data.get('direction', ''),
                property_data.get('trade_type', ''),
                property_data.get('approval_year', 0),
                property_data.get('household_count', 0),
                property_data.get('room_count', 0),
                property_data.get('bathroom_count', 0),
                property_data.get('loan_amount', 0),
                property_data.get('description', ''),
                property_data.get('url', ''),
                now,
                now,
                False
            ))
            
            conn.commit()
            return True
    
    def mark_as_notified(self, property_id: str):
        """
        매물을 알림 완료로 표시
        
        Args:
            property_id: 매물 고유 ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE properties SET notified = 1 WHERE id = ?",
                (property_id,)
            )
            conn.commit()
    
    def get_unnotified_properties(self) -> List[Dict]:
        """
        아직 알림을 보내지 않은 매물 목록 가져오기
        
        Returns:
            매물 정보 리스트
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM properties 
                WHERE notified = 0 
                ORDER BY first_seen DESC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_all_property_ids(self) -> List[str]:
        """
        모든 매물 ID 가져오기
        
        Returns:
            매물 ID 리스트
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM properties")
            return [row[0] for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict:
        """
        데이터베이스 통계 정보
        
        Returns:
            통계 정보 딕셔너리
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM properties")
            total_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM properties WHERE notified = 1")
            notified_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM properties WHERE notified = 0")
            pending_count = cursor.fetchone()[0]
            
            return {
                'total': total_count,
                'notified': notified_count,
                'pending': pending_count
            }


if __name__ == "__main__":
    # 테스트 코드
    db = PropertyDatabase("../data/properties.db")
    print("데이터베이스 초기화 완료")
    print(f"통계: {db.get_stats()}")
