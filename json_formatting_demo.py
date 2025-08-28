#!/usr/bin/env python3
"""JSON 포맷팅 기능 시연 스크립트

bunny-hunter 프로젝트의 깔끔한 JSON 출력을 담당하는 주요 기능들을 설명하고 시연한다.
"""

import json
import sys
import os
sys.path.append('/home/runner/work/bunny-hunter/bunny-hunter/00-main-agent')

# 데모용으로 필요한 함수들만 직접 구현


def demo_json_parsing_strategies():
    """다양한 JSON 파싱 전략 시연"""
    print("=== JSON 파싱 전략 시연 ===\n")
    
    # 1. 깔끔한 JSON 출력 (ensure_ascii=False)
    print("1. ensure_ascii=False로 한글 유지:")
    korean_data = {"메시지": "안녕하세요", "가격": 150000, "상품명": "아이폰 14 프로"}
    clean_json = json.dumps(korean_data, ensure_ascii=False, indent=2)
    print(clean_json)
    print()
    
    # 2. 기본 JSON vs 깔끔한 JSON 비교
    print("2. 기본 JSON (ensure_ascii=True) vs 깔끔한 JSON 비교:")
    print("기본:", json.dumps(korean_data))
    print("깔끔:", json.dumps(korean_data, ensure_ascii=False))
    print()
    
    # 3. 혼합된 출력에서 JSON 추출하는 로직 시뮬레이션
    print("3. 혼합된 출력에서 JSON 추출 (run_container.py 로직):")
    mixed_output = """Starting Docker container...
Loading model...
{"result": "성공", "데이터": {"아이템": "테스트", "개수": 5}}"""
    
    def extract_json_from_mixed_output(raw_output: str):
        """run_container.py의 JSON 추출 로직 재현"""
        raw = raw_output.strip()
        try:
            # 1차: 그대로 JSON 파싱 시도
            return json.loads(raw)
        except json.JSONDecodeError:
            # 2차: stdout에 다른 로그가 섞인 경우 뒤에서부터 JSON 부분을 추출
            # 마지막 줄이 JSON일 가능성이 높으므로 줄별로 시도
            lines = raw.split('\n')
            for line in reversed(lines):
                line = line.strip()
                if line.startswith('{') or line.startswith('['):
                    try:
                        return json.loads(line)
                    except json.JSONDecodeError:
                        continue
            
            # 그래도 실패하면 기존 방식으로 시도
            start = max(raw.rfind("{"), raw.rfind("["))
            if start != -1:
                try:
                    json_part = raw[start:]
                    return json.loads(json_part)
                except json.JSONDecodeError:
                    return None
            return None
    
    extracted = extract_json_from_mixed_output(mixed_output)
    print(f"원본 길이: {len(mixed_output)}")
    print(f"마지막 '{{' 위치: {mixed_output.rfind('{')}")
    print(f"마지막 '[' 위치: {mixed_output.rfind('[')}")
    if extracted:
        print("추출된 JSON:", json.dumps(extracted, ensure_ascii=False, indent=2))
    else:
        print("JSON 추출 실패")
        # 디버깅을 위해 추출 시도한 부분 출력
        start = max(mixed_output.rfind("{"), mixed_output.rfind("["))
        if start != -1:
            json_part = mixed_output[start:]
            print(f"추출 시도한 부분: {repr(json_part)}")
    print()


def demo_safe_json_parsing():
    """안전한 JSON 파싱 시연 (_parse_tool_content 로직)"""
    print("=== 안전한 JSON 파싱 시연 ===\n")
    
    def _parse_tool_content(content):
        """app.py의 _parse_tool_content 함수 재현"""
        if isinstance(content, (dict, list, float, int)):
            return content
        if isinstance(content, str):
            try:
                return json.loads(content)
            except Exception:
                return content
        return content
    
    test_cases = [
        '{"valid": "json", "한글": "지원"}',
        "단순 문자열",
        123,
        {"이미": "딕셔너리"},
        '잘못된 json {',
        '["리스트", "형태", "JSON"]'
    ]
    
    for i, case in enumerate(test_cases, 1):
        result = _parse_tool_content(case)
        print(f"{i}. 입력: {repr(case)}")
        print(f"   결과: {result}")
        print(f"   타입: {type(result).__name__}")
        print()


def demo_json_formatting_in_components():
    """각 컴포넌트별 JSON 포맷팅 특징 시연"""
    print("=== 컴포넌트별 JSON 포맷팅 특징 ===\n")
    
    # 1. 01-search-list 스타일: 검색 결과
    print("1. 01-search-list 스타일 - 검색 결과:")
    search_results = [
        {
            "name": "아이폰 14 프로",
            "description": "상태 좋음, 구성품 포함",
            "url": "https://example.com/item1",
            "price": 1300000.0
        },
        {
            "name": "갤럭시 S23",
            "description": "거의 새것, 케이스 포함",
            "url": "https://example.com/item2", 
            "price": 850000.0
        }
    ]
    print(json.dumps(search_results, ensure_ascii=False, indent=2))
    print()
    
    # 2. 02-gpt-oss-20b-ollama 스타일: AI 응답
    print("2. 02-gpt-oss-20b-ollama 스타일 - AI 응답:")
    ai_response = {
        "text": "안녕하세요! 아이폰 14 프로에 대해 문의드립니다. 현재 판매 중이신지 궁금합니다."
    }
    print(json.dumps(ai_response, ensure_ascii=False, indent=2))
    print()
    
    # 3. 에러 응답 형태
    print("3. 에러 응답 형태:")
    error_response = {"error": "PROMPT env var is empty"}
    print(json.dumps(error_response, ensure_ascii=False, indent=2))
    print()


def demo_json_best_practices():
    """JSON 포맷팅 Best Practices 시연"""
    print("=== JSON 포맷팅 Best Practices ===\n")
    
    print("1. ensure_ascii=False - 한글 문자 유지")
    print("2. indent=2 - 가독성을 위한 들여쓰기 (개발/디버깅용)")
    print("3. flush=True - 즉시 출력 보장")
    print("4. 다단계 파싱 전략 - 로그 혼합 상황 대응")
    print("5. 안전한 타입 검사 - 예외 상황 대응")
    print("6. 일관된 에러 형태 - {\"error\": \"메시지\"}")
    print()
    
    # 실제 사용 예시
    print("실제 사용 예시:")
    sample_data = {
        "검색결과": [
            {"상품명": "테스트 상품", "가격": 100000, "설명": "좋은 상품입니다."}
        ],
        "상태": "성공",
        "타임스탬프": "2024-01-01 12:00:00"
    }
    
    # 개발용 (이쁘게 출력)
    print("개발용 출력:")
    print(json.dumps(sample_data, ensure_ascii=False, indent=2))
    print()
    
    # 프로덕션용 (압축 출력)
    print("프로덕션용 출력:")
    print(json.dumps(sample_data, ensure_ascii=False), flush=True)
    print()


if __name__ == "__main__":
    print("🐰 Bunny Hunter - JSON 포맷팅 기능 시연\n")
    print("이 프로젝트는 '굉장히 깔끔한 형태'의 JSON을 제공합니다.")
    print("아래에서 주요 기능들을 확인해보세요.\n")
    
    demo_json_parsing_strategies()
    demo_safe_json_parsing()
    demo_json_formatting_in_components()
    demo_json_best_practices()
    
    print("🎯 결론: bunny-hunter의 깔끔한 JSON 출력의 비밀")
    print("=" * 50)
    print("1. ensure_ascii=False로 한글 문자 보존")
    print("2. 다단계 파싱으로 로그 혼합 상황 대응")
    print("3. 안전한 타입 검사로 예외 상황 처리")
    print("4. 일관된 형태의 에러 응답")
    print("5. 적절한 들여쓰기와 즉시 출력")