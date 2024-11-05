import os
import json
from datetime import datetime


# 특정 영화의 상영 여부를 확인하는 함수
def check_movie_showing(request: dict):
    # Dialogflow에서 전달된 파라미터 추출
    theater = request.get('queryResult').get('parameters').get('theater')
    movie_title = request.get('queryResult').get('parameters').get('any')

    # branch-가 포함된 키를 찾고 해당 값을 branch 변수로 설정
    parameters = request.get('queryResult').get('parameters')
    branch = next((value for key, value in parameters.items() if 'branch' in key.lower()), None)

    # branch 값이 없거나 지점명이 '점'으로 끝날 경우 제거
    if branch and branch[-1] == '점':
        branch = branch[:-1]

    print(f"[DEBUG] {theater} - {branch} - {movie_title}")

    # 영화 제목의 띄어쓰기를 제거하여 검색용으로 사용
    normalized_movie_title = movie_title.replace(" ", "")

    # 현재 시간
    current_time = datetime.now().strftime("%H:%M")

    # theater 값에 따른 파일 이름 설정
    theater_mapping = {
        "롯데시네마": "lottecinema",
        "메가박스": "megabox",
        "CGV": "cgv"
    }
    theater_key = theater_mapping.get(theater, theater.lower())
    json_file_name = f"{theater_key}_timetable.json"

    # 타임테이블 파일 경로 확인
    current_dir = os.path.dirname(__file__)
    time_table_dir = os.path.join(current_dir, '..', 'timetable')
    json_file_path = os.path.join(time_table_dir, json_file_name)

    # 파일이 존재하지 않을 경우 오류를 콘솔에 출력하고 종료
    if not os.path.exists(json_file_path):
        print(f"[ERROR] '{json_file_name}' 파일이 존재하지 않습니다.")
        return None

    # 파일 로드 및 상영 여부 확인
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    time_table = data['timetable'].get(branch, {})

    # 영화 제목을 포함한 상영 스케줄 확인
    found = False
    for title, showtimes in time_table.items():
        # 상영 중인 영화 제목에서 공백을 제거한 후 비교
        normalized_title = title.replace(" ", "")
        if normalized_movie_title in normalized_title:
            filtered_showtimes = [time for time in showtimes if time > current_time]
            if filtered_showtimes:  # 현재 시간 이후 상영 시간이 있을 때
                found = True
                break

    # 상영 여부에 따른 응답 생성
    if found:
        response_text = f"'{theater} {branch}'에서 '{movie_title}' 영화는 현재 상영 중입니다."
    else:
        response_text = f"'{theater} {branch}'에서 '{movie_title}' 영화는 현재 상영하지 않습니다."

    # Dialogflow 응답 생성
    return {"fulfillmentMessages": [{"text": {"text": [response_text]}}]}


# 특정 영화의 상영 스케줄을 출력하는 함수
def get_movie_schedule(request: dict):
    # outputContexts에서 파라미터 추출
    output_contexts = request.get('queryResult').get('outputContexts', [])
    parameters = {}
    for context in output_contexts:
        parameters.update(context.get('parameters', {}))

    # theater와 movie_title 추출
    theater = parameters.get('theater')
    movie_title = parameters.get('any')

    # branch 파라미터 이름을 동적으로 찾기
    branch = None
    for key, value in parameters.items():
        if 'branch' in key.lower():
            branch = value
            break

    # branch 값이 없거나 지점명이 '점'으로 끝날 경우 '점' 제거
    if branch and branch[-1] == '점':
        branch = branch[:-1]

    # 현재 시간
    current_time = datetime.now().strftime("%H:%M")

    # theater 값에 따른 파일 이름 설정
    theater_mapping = {
        "롯데시네마": "lottecinema",
        "메가박스": "megabox",
        "CGV": "cgv"
    }
    theater_key = theater_mapping.get(theater, theater.lower())
    json_file_name = f"{theater_key}_timetable.json"

    # 타임테이블 파일 경로 확인
    current_dir = os.path.dirname(__file__)
    time_table_dir = os.path.join(current_dir, '..', 'timetable')
    json_file_path = os.path.join(time_table_dir, json_file_name)

    # 파일이 존재하지 않을 경우 기본 오류 메시지 반환
    if not os.path.exists(json_file_path):
        print(f"[ERROR] '{json_file_name}' 파일이 존재하지 않습니다.")
        return {"fulfillmentMessages": [{"text": {"text": ["요청하신 정보를 찾을 수 없습니다."]}}]}

    # 파일 로드 및 스케줄 확인
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    time_table = data['timetable'].get(branch, {})
    normalized_movie_title = movie_title.replace(" ", "")

    # 특정 영화의 상영 스케줄 찾기
    schedule_found = False
    movie_schedule = []
    for title, showtimes in time_table.items():
        normalized_title = title.replace(" ", "")
        if normalized_movie_title in normalized_title:
            # 현재 시간 이후의 상영 시간만 필터링
            filtered_showtimes = [time for time in showtimes if time > current_time]
            if filtered_showtimes:
                movie_schedule = filtered_showtimes
                schedule_found = True
                break

    # 스케줄에 따른 응답 생성
    if schedule_found:
        showtimes_str = " | ".join(movie_schedule)
        response_text = (
            f"'{theater} {branch}'의 '{movie_title}' 상영 스케줄입니다.\n"
            f"{showtimes_str}\n"
            "※ 실제 상영 스케줄과 차이가 있을 수 있습니다. 자세한 상영 스케줄은 영화관 홈페이지를 참고하시길 바랍니다."
        )
    else:
        response_text = f"'{theater} {branch}'에서 '{movie_title}' 영화의 상영 스케줄을 찾을 수 없습니다."

    # Dialogflow 응답 생성
    return {"fulfillmentMessages": [{"text": {"text": [response_text]}}]}
