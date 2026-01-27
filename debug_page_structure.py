"""
네이버 부동산 페이지 구조 확인 (디버깅용)
"""

from playwright.sync_api import sync_playwright
import time

def debug_page():
    """페이지 구조 확인"""
    with sync_playwright() as p:
        # 브라우저 실행
        browser = p.chromium.launch(headless=False)  # 브라우저 창 보이기
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='ko-KR'
        )
        page = context.new_page()
        
        # 페이지 방문
        url = "https://new.land.naver.com/complexes?cortarNo=1168010600&tradeType=B1"
        print(f"페이지 방문 중: {url}")
        
        page.goto(url, wait_until='networkidle', timeout=30000)
        
        print("페이지 로딩 완료!")
        print("\n10초 대기 중 (페이지를 확인하세요)...")
        time.sleep(10)
        
        # HTML 구조 출력
        print("\n페이지 HTML 구조:")
        html = page.content()
        
        # HTML을 파일로 저장
        with open('page_structure.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("HTML 구조를 'page_structure.html' 파일로 저장했습니다!")
        
        # 스크린샷 저장
        page.screenshot(path='screenshot.png')
        print("스크린샷을 'screenshot.png'로 저장했습니다!")
        
        # JavaScript로 페이지 정보 추출
        print("\n페이지 정보 추출 중...")
        
        # 모든 링크 찾기
        links = page.evaluate("""
            () => {
                const links = document.querySelectorAll('a');
                return Array.from(links).slice(0, 10).map(link => ({
                    text: link.textContent?.trim(),
                    href: link.href
                }));
            }
        """)
        
        print(f"\n첫 10개 링크:")
        for i, link in enumerate(links, 1):
            print(f"  {i}. {link['text'][:50]} -> {link['href'][:80]}")
        
        # 주요 클래스 이름 찾기
        classes = page.evaluate("""
            () => {
                const elements = document.querySelectorAll('[class*="complex"]');
                return Array.from(elements).slice(0, 10).map(el => ({
                    tag: el.tagName,
                    class: el.className
                }));
            }
        """)
        
        print(f"\n'complex' 키워드가 포함된 요소들:")
        for i, cls in enumerate(classes, 1):
            print(f"  {i}. <{cls['tag']}> class='{cls['class']}'")
        
        print("\n30초 대기 중 (브라우저를 직접 확인하세요)...")
        time.sleep(30)
        
        # 종료
        browser.close()
        print("\n디버깅 완료!")

if __name__ == "__main__":
    debug_page()
