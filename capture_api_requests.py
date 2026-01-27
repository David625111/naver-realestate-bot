"""
네이버 부동산 실제 API 요청 캡처
브라우저에서 발생하는 모든 네트워크 요청을 기록합니다.
"""

from playwright.sync_api import sync_playwright
import json
import time

def capture_requests():
    """네이버 부동산의 실제 API 요청 캡처"""
    
    api_requests = []
    
    with sync_playwright() as p:
        # 브라우저 실행
        print("=" * 80)
        print("브라우저 실행 중...")
        print("=" * 80)
        
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='ko-KR'
        )
        page = context.new_page()
        
        # 네트워크 요청 감지
        def log_request(request):
            """모든 HTTP 요청 기록"""
            url = request.url
            method = request.method
            
            # API 요청만 필터링
            if 'api' in url or 'ajax' in url or 'land.naver.com' in url:
                request_info = {
                    'method': method,
                    'url': url,
                    'headers': dict(request.headers),
                    'post_data': request.post_data if method == 'POST' else None
                }
                api_requests.append(request_info)
                
                print(f"\n[{method}] {url[:100]}")
                if '?' in url:
                    params = url.split('?')[1]
                    print(f"  Parameters: {params[:200]}")
        
        # 네트워크 요청 리스너 등록
        page.on("request", log_request)
        
        # 1단계: 메인 페이지 방문
        print("\n" + "=" * 80)
        print("1단계: 네이버 부동산 메인 페이지 방문")
        print("=" * 80)
        
        page.goto("https://land.naver.com/", wait_until='networkidle', timeout=30000)
        print("메인 페이지 로딩 완료!")
        time.sleep(3)
        
        # 2단계: 지역 검색 (예: 강남구 대치동)
        print("\n" + "=" * 80)
        print("2단계: 지역 검색 페이지로 이동 중...")
        print("브라우저에서 직접 조작하세요!")
        print("  1) 검색창에 '강남구 대치동' 입력")
        print("  2) 아파트 탭 클릭")
        print("  3) 전세/월세 선택")
        print("=" * 80)
        
        # 사용자가 수동으로 조작할 시간 (60초)
        print("\n60초 대기 중... (직접 페이지를 조작하세요)")
        time.sleep(60)
        
        # 현재 URL 확인
        current_url = page.url
        print(f"\n현재 URL: {current_url}")
        
        # 3단계: 결과 저장
        print("\n" + "=" * 80)
        print("API 요청 수집 결과")
        print("=" * 80)
        
        # API 요청을 파일로 저장
        with open('captured_api_requests.json', 'w', encoding='utf-8') as f:
            json.dump(api_requests, f, ensure_ascii=False, indent=2)
        
        print(f"\n총 {len(api_requests)}개의 API 요청 캡처!")
        print("'captured_api_requests.json' 파일에 저장되었습니다.")
        
        # 중요한 API 요청만 출력
        print("\n주요 API 엔드포인트:")
        unique_urls = set()
        for req in api_requests:
            if 'complexes' in req['url'] or 'articles' in req['url']:
                base_url = req['url'].split('?')[0]
                if base_url not in unique_urls:
                    unique_urls.add(base_url)
                    print(f"  - [{req['method']}] {req['url'][:150]}")
        
        # 현재 페이지 HTML 저장
        html = page.content()
        with open('final_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        # 스크린샷 저장
        page.screenshot(path='final_screenshot.png', full_page=True)
        
        print("\n최종 페이지:")
        print("  - HTML: final_page.html")
        print("  - 스크린샷: final_screenshot.png")
        
        print("\n30초 후 브라우저가 닫힙니다...")
        time.sleep(30)
        
        browser.close()
        print("\n" + "=" * 80)
        print("완료!")
        print("=" * 80)

if __name__ == "__main__":
    print("=" * 80)
    print("네이버 부동산 API 요청 캡처 도구")
    print("=" * 80)
    print()
    print("이 스크립트는 네이버 부동산 페이지에서 발생하는")
    print("모든 API 요청을 캡처하여 올바른 URL과 파라미터를 찾습니다.")
    print()
    print("준비:")
    print("1. 브라우저 창이 열립니다")
    print("2. 60초 동안 직접 페이지를 조작하세요")
    print("3. 모든 네트워크 요청이 기록됩니다")
    print()
    print("시작하려면 Enter를 누르세요...")
    
    input()
    capture_requests()
