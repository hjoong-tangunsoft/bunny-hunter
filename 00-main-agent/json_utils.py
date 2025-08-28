"""JSON 포맷팅 및 파싱 유틸리티 모듈

bunny-hunter 프로젝트에서 사용하는 "굉장히 깔끔한 형태"의 JSON 처리 기능들을 
중앙화된 모듈로 제공한다.
"""

import json
from typing import Any, Union, Dict, List, Optional


def format_json_clean(data: Any, for_development: bool = False) -> str:
    """깔끔한 JSON 문자열 생성
    
    Args:
        data: JSON으로 변환할 데이터
        for_development: True면 들여쓰기 포함, False면 압축 형태
        
    Returns:
        깔끔하게 포맷된 JSON 문자열
    """
    if for_development:
        return json.dumps(data, ensure_ascii=False, indent=2)
    else:
        return json.dumps(data, ensure_ascii=False)


def print_json_clean(data: Any, for_development: bool = False, flush: bool = True) -> None:
    """깔끔한 JSON을 출력
    
    Args:
        data: 출력할 데이터
        for_development: True면 들여쓰기 포함
        flush: 즉시 출력 여부
    """
    json_str = format_json_clean(data, for_development=for_development)
    print(json_str, flush=flush)


def parse_tool_content_safe(content: Any) -> Any:
    """툴 출력을 안전하게 파싱 (app.py의 _parse_tool_content 로직)
    
    Args:
        content: 파싱할 내용
        
    Returns:
        파싱된 데이터 (실패시 원본 반환)
    """
    if isinstance(content, (dict, list, float, int)):
        return content
    if isinstance(content, str):
        try:
            return json.loads(content)
        except Exception:
            return content
    return content


def extract_json_from_mixed_output(raw_output: str) -> Optional[Union[Dict, List]]:
    """혼합된 출력에서 JSON 추출 (run_container.py 로직)
    
    Docker 컨테이너나 기타 프로세스의 stdout에서 로그와 섞인 JSON을 추출한다.
    
    Args:
        raw_output: 혼합된 출력 문자열
        
    Returns:
        추출된 JSON 데이터 (실패시 None)
    """
    raw = raw_output.strip()
    
    try:
        # 1차: 그대로 JSON 파싱 시도
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    
    # 2차: 마지막 줄이 JSON일 가능성이 높으므로 줄별로 시도
    lines = raw.split('\n')
    for line in reversed(lines):
        line = line.strip()
        if line.startswith('{') or line.startswith('['):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    
    # 3차: 뒤에서부터 JSON 부분을 찾아 추출
    start = max(raw.rfind("{"), raw.rfind("["))
    if start != -1:
        try:
            json_part = raw[start:]
            return json.loads(json_part)
        except json.JSONDecodeError:
            pass
    
    return None


def create_error_response(error_message: str) -> Dict[str, str]:
    """일관된 에러 응답 생성
    
    Args:
        error_message: 에러 메시지
        
    Returns:
        {"error": "메시지"} 형태의 딕셔너리
    """
    return {"error": error_message}


def create_success_response(data: Any, message: str = "성공") -> Dict[str, Any]:
    """일관된 성공 응답 생성
    
    Args:
        data: 응답 데이터
        message: 성공 메시지
        
    Returns:
        {"status": "성공", "data": ...} 형태의 딕셔너리
    """
    return {
        "status": message,
        "data": data
    }


def validate_and_clean_json_string(json_string: str) -> Optional[Any]:
    """JSON 문자열 검증 및 정리
    
    Args:
        json_string: 검증할 JSON 문자열
        
    Returns:
        파싱된 데이터 (실패시 None)
    """
    try:
        # 앞뒤 공백 제거 및 파싱
        cleaned = json_string.strip()
        return json.loads(cleaned)
    except (json.JSONDecodeError, AttributeError):
        return None


# === 특화된 포맷터들 ===

def format_search_results(items: List[Dict[str, Any]]) -> str:
    """검색 결과를 깔끔하게 포맷 (01-search-list 스타일)"""
    return format_json_clean(items, for_development=False)


def format_ai_response(text: str) -> str:
    """AI 응답을 깔끔하게 포맷 (02-gpt-oss-20b-ollama 스타일)"""
    response_data = {"text": text}
    return format_json_clean(response_data, for_development=False)


def format_container_output(data: Any) -> str:
    """컨테이너 출력을 깔끔하게 포맷"""
    return format_json_clean(data, for_development=False)


# === 디버깅 및 개발용 함수들 ===

def pretty_print_json(data: Any, title: str = None) -> None:
    """개발용 이쁜 JSON 출력
    
    Args:
        data: 출력할 데이터
        title: 선택적 제목
    """
    if title:
        print(f"\n=== {title} ===")
    print_json_clean(data, for_development=True)
    print()


def compare_json_formats(data: Any) -> None:
    """JSON 포맷 비교 출력 (ensure_ascii True vs False)"""
    print("기본 JSON (ensure_ascii=True):")
    print(json.dumps(data, ensure_ascii=True))
    print("\n깔끔한 JSON (ensure_ascii=False):")
    print(json.dumps(data, ensure_ascii=False))
    print()


# === 전체 시스템에서 사용하는 표준 함수들 ===

def get_clean_json_response(data: Any, success: bool = True, message: str = None) -> str:
    """시스템 전체에서 사용할 표준 JSON 응답 생성
    
    Args:
        data: 응답 데이터
        success: 성공 여부
        message: 추가 메시지
        
    Returns:
        표준화된 JSON 응답 문자열
    """
    if success:
        if message:
            response = create_success_response(data, message)
        else:
            response = data if isinstance(data, dict) else {"result": data}
    else:
        response = create_error_response(str(data))
    
    return format_json_clean(response, for_development=False)


# === 모듈 테스트 함수 ===

def test_json_utils():
    """JSON 유틸리티 기능 테스트"""
    print("🧪 JSON Utils 테스트 시작\n")
    
    # 1. 기본 포맷팅 테스트
    test_data = {"메시지": "테스트", "숫자": 12345, "리스트": ["항목1", "항목2"]}
    pretty_print_json(test_data, "기본 포맷팅 테스트")
    
    # 2. 혼합 출력 파싱 테스트
    mixed_output = """로그 메시지 1
로그 메시지 2
{"결과": "성공", "데이터": {"값": 100}}"""
    
    parsed = extract_json_from_mixed_output(mixed_output)
    pretty_print_json(parsed, "혼합 출력 파싱 테스트")
    
    # 3. 안전한 파싱 테스트
    test_cases = [
        '{"json": "문자열"}',
        "일반 문자열",
        {"dict": "객체"},
        '["배열", "형태"]'
    ]
    
    print("=== 안전한 파싱 테스트 ===")
    for case in test_cases:
        result = parse_tool_content_safe(case)
        print(f"입력: {repr(case)} -> 결과: {result} ({type(result).__name__})")
    
    print("\n✅ 모든 테스트 완료!")


if __name__ == "__main__":
    test_json_utils()