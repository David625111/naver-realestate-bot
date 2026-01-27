"""
네이버 부동산 직접 접속 테스트
"""

import requests
import json

# 테스트 1: 메인 페이지 접속
print("=" * 60)
print("테스트 1: 네이버 부동산 메인 페이지 접속")
print("=" * 60)

url = "https://new.land.naver.com"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
}

session = requests.Session()
session.headers.update(headers)

try:
    response = session.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    
    print(f"\nCookies:")
    cookies = session.cookies.get_dict()
    if cookies:
        for key, value in cookies.items():
            print(f"  {key}: {value[:50]}...")
    else:
        print("  (쿠키 없음)")
    
    print(f"\nResponse Length: {len(response.text)} bytes")
    print(f"Response Preview: {response.text[:200]}...")
    
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("테스트 2: API 엔드포인트 직접 접속")
print("=" * 60)

# 테스트 2: API 직접 접속
api_url = "https://new.land.naver.com/api/complexes"
params = {
    'cortarNo': '1168010600',  # 강남구 대치동
    'realEstateType': 'APT',
    'tradeType': 'B1',  # 전세
}

try:
    response = session.get(api_url, params=params, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response Keys: {list(data.keys())}")
        if 'complexList' in data:
            print(f"Complex Count: {len(data['complexList'])}")
    else:
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
