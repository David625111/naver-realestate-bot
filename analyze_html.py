"""HTML 파일에서 데이터 구조 분석"""
import re
from collections import Counter

with open('desktop_page_1114016200_B1.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("=" * 80)
print("HTML 분석 결과")
print("=" * 80)

# 1. 모든 클래스 이름 찾기 (complex 포함)
complex_classes = re.findall(r'class="([^"]*complex[^"]*)"', html, re.IGNORECASE)
if complex_classes:
    print(f"\n'complex' 포함 클래스 (상위 20개):")
    class_counter = Counter(complex_classes)
    for cls, count in class_counter.most_common(20):
        print(f"  - {cls} ({count}개)")

# 2. 모든 클래스 이름 찾기 (list 포함)
list_classes = re.findall(r'class="([^"]*list[^"]*)"', html, re.IGNORECASE)
if list_classes:
    print(f"\n'list' 포함 클래스 (상위 20개):")
    class_counter = Counter(list_classes)
    for cls, count in class_counter.most_common(20):
        print(f"  - {cls} ({count}개)")

# 3. 모든 클래스 이름 찾기 (item 포함)
item_classes = re.findall(r'class="([^"]*item[^"]*)"', html, re.IGNORECASE)
if item_classes:
    print(f"\n'item' 포함 클래스 (상위 20개):")
    class_counter = Counter(item_classes)
    for cls, count in class_counter.most_common(20):
        print(f"  - {cls} ({count}개)")

# 4. data- 속성 찾기
data_attrs = re.findall(r'data-([a-z-]+)=', html, re.IGNORECASE)
if data_attrs:
    print(f"\ndata- 속성 (상위 20개):")
    attr_counter = Counter(data_attrs)
    for attr, count in attr_counter.most_common(20):
        print(f"  - data-{attr} ({count}개)")

print("\n" + "=" * 80)
