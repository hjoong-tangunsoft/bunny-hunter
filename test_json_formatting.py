#!/usr/bin/env python3
"""JSON 포맷팅 기능 테스트 스위트

bunny-hunter의 JSON 포맷팅 기능들을 검증한다.
"""

import json
import sys
import os
import unittest
from io import StringIO

# 테스트할 모듈 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '00-main-agent'))

from json_utils import (
    format_json_clean,
    parse_tool_content_safe,
    extract_json_from_mixed_output,
    create_error_response,
    create_success_response,
    validate_and_clean_json_string,
    get_clean_json_response
)


class TestJSONFormatting(unittest.TestCase):
    """JSON 포맷팅 기능 테스트"""

    def test_format_json_clean_korean(self):
        """한글 문자 보존 테스트"""
        data = {"메시지": "안녕하세요", "가격": 150000}
        
        # 개발용 (들여쓰기)
        result_dev = format_json_clean(data, for_development=True)
        self.assertIn('"메시지": "안녕하세요"', result_dev)
        self.assertIn('\n', result_dev)  # 들여쓰기 확인
        
        # 프로덕션용 (압축)
        result_prod = format_json_clean(data, for_development=False)
        self.assertIn('"메시지":"안녕하세요"', result_prod.replace(' ', ''))
        self.assertNotIn('\n', result_prod)  # 들여쓰기 없음

    def test_format_json_vs_standard(self):
        """표준 json.dumps와 비교"""
        data = {"한글": "테스트", "영어": "test"}
        
        # 표준 방식 (한글이 이스케이프됨)
        standard = json.dumps(data)
        self.assertIn('\\u', standard)
        
        # 깔끔한 방식 (한글 보존)
        clean = format_json_clean(data)
        self.assertNotIn('\\u', clean)
        self.assertIn('한글', clean)

    def test_parse_tool_content_safe(self):
        """안전한 툴 컨텐츠 파싱 테스트"""
        
        # JSON 문자열 파싱
        json_str = '{"key": "value", "한글": "값"}'
        result = parse_tool_content_safe(json_str)
        self.assertEqual(result, {"key": "value", "한글": "값"})
        
        # 이미 파싱된 딕셔너리
        dict_data = {"already": "parsed"}
        result = parse_tool_content_safe(dict_data)
        self.assertEqual(result, dict_data)
        
        # 일반 문자열 (JSON 아님)
        plain_str = "단순 문자열"
        result = parse_tool_content_safe(plain_str)
        self.assertEqual(result, plain_str)
        
        # 숫자
        number = 123
        result = parse_tool_content_safe(number)
        self.assertEqual(result, number)
        
        # 잘못된 JSON
        invalid_json = '{"invalid": json}'
        result = parse_tool_content_safe(invalid_json)
        self.assertEqual(result, invalid_json)

    def test_extract_json_from_mixed_output(self):
        """혼합 출력에서 JSON 추출 테스트"""
        
        # 순수 JSON
        pure_json = '{"result": "success"}'
        result = extract_json_from_mixed_output(pure_json)
        self.assertEqual(result, {"result": "success"})
        
        # 로그와 혼합된 JSON (마지막 줄)
        mixed_output = """Starting process...
Loading data...
{"result": "성공", "data": {"count": 5}}"""
        result = extract_json_from_mixed_output(mixed_output)
        self.assertEqual(result, {"result": "성공", "data": {"count": 5}})
        
        # 복잡한 혼합 출력
        complex_mixed = """Log line 1
Log line 2
Some other output
{"final": "result", "korean": "한글"}
"""
        result = extract_json_from_mixed_output(complex_mixed)
        self.assertEqual(result, {"final": "result", "korean": "한글"})
        
        # JSON 배열
        array_mixed = """Processing...
Done
["item1", "item2", "한글항목"]"""
        result = extract_json_from_mixed_output(array_mixed)
        self.assertEqual(result, ["item1", "item2", "한글항목"])
        
        # JSON이 없는 경우
        no_json = "Only log messages here\nNo JSON at all"
        result = extract_json_from_mixed_output(no_json)
        self.assertIsNone(result)

    def test_error_and_success_responses(self):
        """에러 및 성공 응답 생성 테스트"""
        
        # 에러 응답
        error_resp = create_error_response("Something went wrong")
        self.assertEqual(error_resp, {"error": "Something went wrong"})
        
        # 성공 응답
        data = {"items": [1, 2, 3]}
        success_resp = create_success_response(data)
        expected = {"status": "성공", "data": {"items": [1, 2, 3]}}
        self.assertEqual(success_resp, expected)
        
        # 커스텀 메시지 성공 응답
        custom_success = create_success_response(data, "처리완료")
        expected_custom = {"status": "처리완료", "data": {"items": [1, 2, 3]}}
        self.assertEqual(custom_success, expected_custom)

    def test_validate_and_clean_json_string(self):
        """JSON 문자열 검증 및 정리 테스트"""
        
        # 정상적인 JSON
        valid_json = '  {"clean": "me"}  '
        result = validate_and_clean_json_string(valid_json)
        self.assertEqual(result, {"clean": "me"})
        
        # 잘못된 JSON
        invalid_json = '{"invalid": json'
        result = validate_and_clean_json_string(invalid_json)
        self.assertIsNone(result)
        
        # None 입력
        result = validate_and_clean_json_string(None)
        self.assertIsNone(result)

    def test_get_clean_json_response(self):
        """표준 JSON 응답 생성 테스트"""
        
        # 성공 응답 (딕셔너리 데이터)
        data = {"result": "완료"}
        success_response = get_clean_json_response(data, success=True)
        parsed = json.loads(success_response)
        self.assertEqual(parsed, {"result": "완료"})
        
        # 성공 응답 (메시지 포함)
        success_with_message = get_clean_json_response(data, success=True, message="작업완료")
        parsed = json.loads(success_with_message)
        expected = {"status": "작업완료", "data": {"result": "완료"}}
        self.assertEqual(parsed, expected)
        
        # 에러 응답
        error_response = get_clean_json_response("오류 발생", success=False)
        parsed = json.loads(error_response)
        self.assertEqual(parsed, {"error": "오류 발생"})

    def test_real_world_scenarios(self):
        """실제 사용 시나리오 테스트"""
        
        # 시나리오 1: 당근마켓 검색 결과 형태
        search_results = [
            {
                "name": "아이폰 14 프로",
                "description": "상태 좋음, 구성품 포함",
                "url": "https://example.com/item1",
                "price": 1300000.0
            }
        ]
        json_str = format_json_clean(search_results)
        # 한글이 제대로 보존되는지 확인
        self.assertIn("아이폰 14 프로", json_str)
        self.assertIn("상태 좋음", json_str)
        
        # 시나리오 2: AI 응답 형태
        ai_response = {"text": "안녕하세요! 문의 주신 내용에 대해 답변드립니다."}
        json_str = format_json_clean(ai_response)
        self.assertIn("안녕하세요", json_str)
        
        # 시나리오 3: Docker 컨테이너 혼합 출력
        container_output = """2024-01-01 12:00:00 - Starting container
2024-01-01 12:00:01 - Loading model
2024-01-01 12:00:05 - Ready
{"text": "모델이 준비되었습니다. 요청을 처리할 수 있습니다."}"""
        
        extracted = extract_json_from_mixed_output(container_output)
        self.assertIsNotNone(extracted)
        self.assertEqual(extracted["text"], "모델이 준비되었습니다. 요청을 처리할 수 있습니다.")


class TestJSONFormattingIntegration(unittest.TestCase):
    """통합 테스트"""

    def test_end_to_end_workflow(self):
        """전체 워크플로우 테스트"""
        
        # 1. 외부 프로세스 출력 시뮬레이션
        raw_output = """Starting process...
Loading configuration...
{"results": [{"name": "테스트 상품", "price": 50000}], "status": "완료"}"""
        
        # 2. JSON 추출
        extracted = extract_json_from_mixed_output(raw_output)
        self.assertIsNotNone(extracted)
        
        # 3. 안전한 파싱 (이미 추출된 상태지만 테스트)
        safe_parsed = parse_tool_content_safe(extracted)
        self.assertEqual(safe_parsed, extracted)
        
        # 4. 깔끔한 형태로 재포맷
        clean_output = format_json_clean(safe_parsed)
        
        # 5. 최종 결과 검증
        final_data = json.loads(clean_output)
        self.assertEqual(final_data["status"], "완료")
        self.assertEqual(final_data["results"][0]["name"], "테스트 상품")

    def test_error_handling_chain(self):
        """에러 처리 체인 테스트"""
        
        # 1. 잘못된 출력
        bad_output = "Error: Process failed\nNo JSON here"
        
        # 2. JSON 추출 실패
        extracted = extract_json_from_mixed_output(bad_output)
        self.assertIsNone(extracted)
        
        # 3. 에러 응답 생성
        error_response = create_error_response("JSON 추출 실패")
        
        # 4. 깔끔한 에러 출력
        error_json = format_json_clean(error_response)
        
        # 5. 검증
        parsed_error = json.loads(error_json)
        self.assertEqual(parsed_error["error"], "JSON 추출 실패")


def run_json_formatting_tests():
    """JSON 포맷팅 테스트 실행"""
    print("🧪 JSON 포맷팅 기능 테스트 시작\n")
    
    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 테스트 클래스들 추가
    suite.addTests(loader.loadTestsFromTestCase(TestJSONFormatting))
    suite.addTests(loader.loadTestsFromTestCase(TestJSONFormattingIntegration))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 요약
    print(f"\n📊 테스트 결과:")
    print(f"✅ 성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    if result.failures:
        print(f"❌ 실패: {len(result.failures)}")
    if result.errors:
        print(f"💥 에러: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_json_formatting_tests()
    sys.exit(0 if success else 1)