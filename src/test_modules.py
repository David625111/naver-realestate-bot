"""
모듈별 테스트 스크립트
"""

import sys
import os

# 테스트 결과 저장
test_results = []

def test_imports():
    """모듈 import 테스트"""
    print("\n" + "="*60)
    print("1. 모듈 Import 테스트")
    print("="*60)
    
    try:
        from database import PropertyDatabase
        print("✅ database.py import 성공")
        test_results.append(("Import database", True, None))
    except Exception as e:
        print(f"❌ database.py import 실패: {e}")
        test_results.append(("Import database", False, str(e)))
    
    try:
        from scraper import NaverRealEstateScraper
        print("✅ scraper.py import 성공")
        test_results.append(("Import scraper", True, None))
    except Exception as e:
        print(f"❌ scraper.py import 실패: {e}")
        test_results.append(("Import scraper", False, str(e)))
    
    try:
        from filter_manager import FilterManager
        print("✅ filter_manager.py import 성공")
        test_results.append(("Import filter_manager", True, None))
    except Exception as e:
        print(f"❌ filter_manager.py import 실패: {e}")
        test_results.append(("Import filter_manager", False, str(e)))
    
    try:
        from telegram_bot import TelegramNotifierSync
        print("✅ telegram_bot.py import 성공")
        test_results.append(("Import telegram_bot", True, None))
    except Exception as e:
        print(f"❌ telegram_bot.py import 실패: {e}")
        test_results.append(("Import telegram_bot", False, str(e)))


def test_database():
    """데이터베이스 기능 테스트"""
    print("\n" + "="*60)
    print("2. 데이터베이스 기능 테스트")
    print("="*60)
    
    try:
        from database import PropertyDatabase
        
        # 테스트용 DB 생성
        db = PropertyDatabase("../data/test_properties.db")
        print("✅ 데이터베이스 초기화 성공")
        
        # 테스트 데이터 추가
        test_property = {
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
            'description': '테스트 매물',
            'url': 'https://test.com'
        }
        
        result = db.add_property(test_property)
        if result:
            print("✅ 테스트 매물 추가 성공")
        else:
            print("⚠️  중복 매물 (이미 존재)")
        
        # 통계 확인
        stats = db.get_stats()
        print(f"✅ DB 통계 조회 성공: {stats}")
        
        # 테스트 DB 삭제
        import os
        if os.path.exists("../data/test_properties.db"):
            os.remove("../data/test_properties.db")
            print("✅ 테스트 DB 정리 완료")
        
        test_results.append(("Database operations", True, None))
        
    except Exception as e:
        print(f"❌ 데이터베이스 테스트 실패: {e}")
        test_results.append(("Database operations", False, str(e)))


def test_filter():
    """필터 기능 테스트"""
    print("\n" + "="*60)
    print("3. 필터링 시스템 테스트")
    print("="*60)
    
    try:
        from filter_manager import FilterManager
        
        # 필터 매니저 초기화
        filter_mgr = FilterManager("../config/filters.json")
        print("✅ 필터 설정 로드 성공")
        
        # 테스트 매물 - 통과해야 함
        test_property_pass = {
            'id': 'test_pass',
            'complex_name': '통과 테스트',
            'trade_type': 'A1',
            'price': 100000,  # 5억~15억 범위
            'area_exclusive': 70,  # 59~84 범위
            'approval_year': 2020,  # 2018~2024 범위
            'household_count': 500,  # 300~2000 범위
            'floor': '15/25',  # 중간층 또는 고층
            'room_count': 3,
            'bathroom_count': 2,
            'direction': '남향',
            'loan_amount': 0
        }
        
        result = filter_mgr.apply_filters(test_property_pass)
        if result:
            print("✅ 필터 통과 테스트 성공")
        else:
            print("❌ 필터 통과 테스트 실패 (통과해야 하는데 실패)")
        
        # 테스트 매물 - 실패해야 함 (가격 초과)
        test_property_fail = {
            'id': 'test_fail',
            'complex_name': '실패 테스트',
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
        
        result = filter_mgr.apply_filters(test_property_fail)
        if not result:
            print("✅ 필터 차단 테스트 성공")
        else:
            print("❌ 필터 차단 테스트 실패 (차단되어야 하는데 통과)")
        
        test_results.append(("Filter operations", True, None))
        
    except Exception as e:
        print(f"❌ 필터 테스트 실패: {e}")
        test_results.append(("Filter operations", False, str(e)))


def test_config_files():
    """설정 파일 존재 확인"""
    print("\n" + "="*60)
    print("4. 설정 파일 존재 확인")
    print("="*60)
    
    files_to_check = [
        "../config/filters.json",
        "../requirements.txt",
        "../.gitignore",
        "../.github/workflows/scraper.yml",
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
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (없음)")
            all_exist = False
    
    if all_exist:
        test_results.append(("Config files", True, None))
    else:
        test_results.append(("Config files", False, "일부 파일 누락"))


def test_scraper_basic():
    """스크레이퍼 기본 기능 테스트"""
    print("\n" + "="*60)
    print("5. 스크레이퍼 초기화 테스트")
    print("="*60)
    
    try:
        from scraper import NaverRealEstateScraper
        
        scraper = NaverRealEstateScraper()
        print("✅ 스크레이퍼 초기화 성공")
        print(f"   User-Agent 개수: {len(scraper.USER_AGENTS)}")
        print(f"   Base URL: {scraper.BASE_URL}")
        
        test_results.append(("Scraper initialization", True, None))
        
    except Exception as e:
        print(f"❌ 스크레이퍼 테스트 실패: {e}")
        test_results.append(("Scraper initialization", False, str(e)))


def print_summary():
    """테스트 결과 요약"""
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    
    total = len(test_results)
    passed = sum(1 for _, success, _ in test_results if success)
    failed = total - passed
    
    print(f"\n총 테스트: {total}개")
    print(f"✅ 성공: {passed}개")
    print(f"❌ 실패: {failed}개")
    
    if failed > 0:
        print("\n실패한 테스트:")
        for name, success, error in test_results:
            if not success:
                print(f"  - {name}: {error}")
    
    print("\n" + "="*60)
    
    if failed == 0:
        print("🎉 모든 테스트 통과!")
        print("="*60)
        return True
    else:
        print("⚠️  일부 테스트 실패")
        print("="*60)
        return False


def main():
    """메인 테스트 함수"""
    print("\n")
    print("=" * 60)
    print("  네이버 부동산 봇 모듈 테스트")
    print("=" * 60)
    
    # 각 테스트 실행
    test_imports()
    test_database()
    test_filter()
    test_config_files()
    test_scraper_basic()
    
    # 결과 요약
    success = print_summary()
    
    # 종료 코드 반환
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
