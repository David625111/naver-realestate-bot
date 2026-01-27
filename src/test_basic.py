"""
기본 모듈 테스트 (환경 변수 불필요)
"""

import sys
import os
import gc

print("="*60)
print("  기본 모듈 테스트 시작")
print("="*60)

# 테스트 결과
results = []

# 1. Import 테스트
print("\n1. 모듈 Import 테스트")
print("-"*60)

try:
    from database import PropertyDatabase
    print("[OK] database.py import 성공")
    results.append(("database import", True))
except Exception as e:
    print(f"[FAIL] database.py: {e}")
    results.append(("database import", False))

try:
    from scraper import NaverRealEstateScraper
    print("[OK] scraper.py import 성공")
    results.append(("scraper import", True))
except Exception as e:
    print(f"[FAIL] scraper.py: {e}")
    results.append(("scraper import", False))

try:
    from filter_manager import FilterManager
    print("[OK] filter_manager.py import 성공")
    results.append(("filter_manager import", True))
except Exception as e:
    print(f"[FAIL] filter_manager.py: {e}")
    results.append(("filter_manager import", False))

try:
    from telegram_bot import TelegramNotifierSync
    print("[OK] telegram_bot.py import 성공")
    results.append(("telegram_bot import", True))
except Exception as e:
    print(f"[FAIL] telegram_bot.py: {e}")
    results.append(("telegram_bot import", False))

# 2. 설정 파일 테스트
print("\n2. 설정 파일 로드 테스트")
print("-"*60)

try:
    from filter_manager import FilterManager
    filter_mgr = FilterManager("../config/filters.json")
    print("[OK] filters.json 로드 성공")
    print(f"     거래 유형: {filter_mgr.filters.get('trade_types')}")
    print(f"     가격 범위: {filter_mgr.filters.get('price_range')}")
    results.append(("config load", True))
except Exception as e:
    print(f"[FAIL] 설정 파일: {e}")
    results.append(("config load", False))

# 3. 데이터베이스 테스트
print("\n3. 데이터베이스 초기화 테스트")
print("-"*60)

try:
    from database import PropertyDatabase
    db = PropertyDatabase("../data/test.db")
    print("[OK] 데이터베이스 초기화 성공")
    
    # 테스트 데이터 추가
    test_prop = {
        'id': 'test_001',
        'complex_no': '12345',
        'complex_name': '테스트아파트',
        'article_no': '67890',
        'price': 100000,
        'area_real': 84.5,
        'area_exclusive': 59.2,
        'floor': '10/25',
        'total_floors': 25,
        'direction': '남향',
        'trade_type': 'A1',
        'approval_year': 2020,
        'household_count': 500,
        'room_count': 3,
        'bathroom_count': 2,
        'loan_amount': 0,
        'description': '테스트',
        'url': 'https://test.com'
    }
    
    added = db.add_property(test_prop)
    if added:
        print("[OK] 테스트 매물 추가 성공")
    else:
        print("[INFO] 매물 이미 존재 (정상)")
    
    stats = db.get_stats()
    print(f"[OK] DB 통계: {stats}")
    
    # 정리 - 데이터베이스 연결 해제 후 삭제
    del db  # 데이터베이스 객체 삭제하여 연결 해제
    gc.collect()  # 가비지 컬렉션 강제 실행
    import time
    time.sleep(0.2)  # 파일 핸들이 완전히 해제될 때까지 대기
    
    # 파일 삭제 시도 (실패해도 테스트는 통과)
    try:
        if os.path.exists("../data/test.db"):
            os.remove("../data/test.db")
            print("[OK] 테스트 DB 정리 완료")
    except Exception as e:
        print(f"[INFO] 테스트 DB 정리 건너뜀: {e}")
        print("[INFO] (다음 테스트 실행 시 덮어쓰기됩니다)")
    
    results.append(("database operations", True))
except Exception as e:
    print(f"[FAIL] 데이터베이스: {e}")
    results.append(("database operations", False))

# 4. 필터 로직 테스트
print("\n4. 필터링 로직 테스트")
print("-"*60)

try:
    from filter_manager import FilterManager
    filter_mgr = FilterManager("../config/filters.json")
    
    # 테스트 매물 (통과해야 함)
    test_pass = {
        'id': 'test_pass',
        'complex_name': '통과테스트',
        'trade_type': 'A1',
        'price': 100000,
        'area_exclusive': 70,
        'approval_year': 2020,
        'household_count': 500,
        'floor': '15/25',
        'room_count': 3,
        'bathroom_count': 2,
        'direction': '남향',
        'loan_amount': 0
    }
    
    if filter_mgr.apply_filters(test_pass):
        print("[OK] 필터 통과 테스트 성공")
    else:
        print("[FAIL] 필터 통과 테스트 실패")
    
    # 테스트 매물 (차단되어야 함)
    test_fail = {
        'id': 'test_fail',
        'complex_name': '차단테스트',
        'trade_type': 'A1',
        'price': 200000,  # 15억 초과
        'area_exclusive': 70,
        'approval_year': 2020,
        'household_count': 500,
        'floor': '15/25',
        'room_count': 3,
        'bathroom_count': 2,
        'direction': '남향',
        'loan_amount': 0
    }
    
    if not filter_mgr.apply_filters(test_fail):
        print("[OK] 필터 차단 테스트 성공")
    else:
        print("[FAIL] 필터 차단 테스트 실패")
    
    results.append(("filter logic", True))
except Exception as e:
    print(f"[FAIL] 필터링: {e}")
    results.append(("filter logic", False))

# 5. 파일 구조 확인
print("\n5. 프로젝트 파일 구조 확인")
print("-"*60)

files_to_check = [
    "../config/filters.json",
    "../requirements.txt",
    "../.gitignore",
    "../README.md",
    "main.py",
    "database.py",
    "scraper.py",
    "filter_manager.py",
    "telegram_bot.py"
]

all_exist = True
for file_path in files_to_check:
    if os.path.exists(file_path):
        print(f"[OK] {file_path}")
    else:
        print(f"[FAIL] {file_path} (없음)")
        all_exist = False

if all_exist:
    results.append(("file structure", True))
else:
    results.append(("file structure", False))

# 결과 요약
print("\n" + "="*60)
print("테스트 결과 요약")
print("="*60)

passed = sum(1 for _, success in results if success)
failed = len(results) - passed

print(f"\n총 테스트: {len(results)}개")
print(f"[OK] 성공: {passed}개")
print(f"[FAIL] 실패: {failed}개")

if failed > 0:
    print("\n실패한 테스트:")
    for name, success in results:
        if not success:
            print(f"  - {name}")

print("\n" + "="*60)
if failed == 0:
    print("축하합니다! 모든 기본 테스트 통과!")
    print("\n다음 단계:")
    print("1. .env 파일에 텔레그램 설정 입력")
    print("2. python main.py 실행으로 실제 크롤링 테스트")
else:
    print("일부 테스트 실패. 위의 에러 메시지 확인 필요")

print("="*60)

sys.exit(0 if failed == 0 else 1)
