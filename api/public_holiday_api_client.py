from ftplib import print_line

import requests
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

BASE_URL = "https://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService"
SERVICE_KEY = os.getenv("SERVICE_KEY")
if SERVICE_KEY:
    SERVICE_KEY = SERVICE_KEY.strip()  # 공백 및 줄바꿈 제거

if not SERVICE_KEY:
    print("⚠️  경고: SERVICE_KEY가 .env 파일에 설정되지 않았습니다.")
    print("   공공데이터포털(https://www.data.go.kr)에서 API 키를 발급받아 .env 파일에 추가하세요.")

def fetch_holiday_data(endpoint: str, year: int, month: int) -> dict:
    url = f"{BASE_URL}/{endpoint}"
    
    # 공공데이터포털 API는 ServiceKey를 인코딩하지 않고 그대로 전달해야 함
    # Java의 DefaultUriBuilderFactory.EncodingMode.NONE과 동일한 효과
    # 다른 파라미터는 정상적으로 인코딩하고, ServiceKey만 인코딩 없이 직접 추가
    from urllib.parse import urlencode, quote
    
    # ServiceKey를 제외한 다른 파라미터만 인코딩
    other_params = {
        "solYear": year,
        "solMonth": f"{month:02d}",
        "_type": "json",
        "numOfRows": 100
    }
    query_string = urlencode(other_params)
    
    # ServiceKey를 인코딩하지 않고 그대로 추가 (Java의 EncodingMode.NONE과 동일)
    # 공공데이터포털 API는 ServiceKey가 인코딩되면 인식하지 못함
    if SERVICE_KEY:
        # ServiceKey는 인코딩하지 않고 그대로 URL에 추가
        full_url = f"{url}?{query_string}&ServiceKey={SERVICE_KEY}"
    else:
        full_url = f"{url}?{query_string}"
    
    print(f"요청 URL: {url}")
    print(f"파라미터: solYear={year}, solMonth={month:02d}")
    print(f"ServiceKey 길이: {len(SERVICE_KEY) if SERVICE_KEY else 0}자")
    print(f"ServiceKey 처리: 인코딩 없이 그대로 전달 (EncodingMode.NONE)")
    
    # ServiceKey를 인코딩하지 않고 그대로 전달
    response = requests.get(full_url, verify=certifi.where())
    
    # 디버깅: 실제 요청된 URL 확인 (ServiceKey는 마스킹)
    actual_url = response.url
    if SERVICE_KEY and SERVICE_KEY in actual_url:
        masked_url = actual_url.replace(SERVICE_KEY, "*" * 20)
        print(f"실제 요청 URL (ServiceKey 마스킹): {masked_url}")
    else:
        print(f"실제 요청 URL: {actual_url}")
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        status_code = response.status_code
        actual_url = response.url  # 실제 요청된 URL (인코딩 후)
        print(f"\n❌ HTTP 에러 발생: {status_code}")
        print(f"요청 URL: {actual_url}")
        print(f"에러 메시지: {e}")
        if status_code == 401:
            print("\n⚠️  401 인증 오류 해결 방법:")
            print("1. 공공데이터포털(https://www.data.go.kr) 마이페이지에서 확인:")
            print("   - API 키가 정상적으로 발급되었는지 확인")
            print("   - 해당 API 서비스(SpcdeInfoService) 활용 신청이 승인되었는지 확인")
            print("2. .env 파일의 SERVICE_KEY 확인:")
            print("   - SERVICE_KEY가 올바르게 설정되었는지 확인")
            print("   - API 키에 공백이나 줄바꿈이 포함되지 않았는지 확인")
            print("   - 인코딩된 키(Encoding)와 디코딩된 키(Decoding) 중 올바른 것을 사용")
            print("3. API 키 재발급:")
            print("   - 문제가 지속되면 공공데이터포털에서 새 API 키를 발급받아 사용")
        elif status_code == 403:
            print("\n⚠️  403 권한 없음 오류 해결 방법:")
            print("403 Forbidden은 API 키는 인식되지만 해당 리소스에 접근할 권한이 없다는 의미입니다.")
            print("\n1. 활용기간 확인:")
            print("   - 공공데이터포털 마이페이지에서 활용기간 확인")
            print("   - 활용기간이 시작되지 않았거나 만료되었으면 403 에러 발생")
            print("   - 예: 활용기간이 2025-05-20부터 시작되면 그 이전에는 사용 불가")
            print("\n2. 공공데이터포털 마이페이지에서 확인:")
            print("   - 마이페이지 → 개발계정 → 인증키 관리")
            print("   - 해당 API 서비스(SpcdeInfoService)에 대한 활용 신청 상태 확인")
            print("   - '승인' 상태인지 확인 (승인 대기 중이면 403 에러 발생)")
            print("   - 활용 신청이 없으면 새로 신청 필요")
            print("\n3. API 서비스 페이지에서 확인:")
            print("   - https://www.data.go.kr 에서 'SpcdeInfoService' 검색")
            print("   - 해당 서비스 페이지에서 '활용신청' 버튼 클릭")
            print("   - 활용 신청 후 승인 대기 (보통 즉시 또는 몇 시간 내 승인)")
            print("\n4. 다른 가능한 원인:")
            print("   - 일일 호출 제한 초과 (공공데이터포털에서 확인)")
            print("   - API 키가 해당 서비스에 연결되지 않음")
            print("   - 서비스가 일시적으로 중단되었거나 변경됨")
            print("   - ServiceKey 인코딩 문제 (현재 코드는 인코딩하지 않고 그대로 전달)")
            print("\n5. 테스트 방법:")
            print("   - 공공데이터포털의 'API 활용가이드'에서 샘플 URL로 직접 테스트")
            print("   - 브라우저에서 직접 URL 호출해보기")
        print(f"\n응답 내용: {response.text[:500]}")
        return {"error": f"HTTP {status_code}", "status_code": status_code, "body": response.text}
    except requests.exceptions.JSONDecodeError:
        print(f"JSON 파싱 실패: {url}")
        print(f"응답 내용: {response.text[:200]}")
        return {"error": "Invalid JSON", "body": response.text}
    except requests.exceptions.RequestException as e:
        print(f"요청 실패: {url}")
        print(f"에러: {e}")
        return {"error": str(e)}

def get_rest_holidays(year: int, month: int) -> dict:
    return fetch_holiday_data("getRestDeInfo", year, month)

def get_anniversaries(year: int, month: int) -> dict:
    return fetch_holiday_data("getAnniversaryInfo", year, month)

def get_24_divisions(year: int, month: int) -> dict:
    return fetch_holiday_data("get24DivisionsInfo", year, month)

def get_sundry_days(year: int, month: int) -> dict:
    return fetch_holiday_data("getSundryDayInfo", year, month)