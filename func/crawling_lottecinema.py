import requests
import os
import json
from datetime import datetime


# 답변 생성 메서드
def generate_response(theater_nm: str, branch_nm: str, time_table: dict):
    # 현재 시간 가져오기
    current_time = datetime.now().strftime("%H:%M")
    response_texts = []

    # 상영 스케줄을 필터링하여 현재 시간 이후의 상영 정보만 남기기
    filtered_time_table = {}
    for title, showtimes in time_table.items():
        filtered_showtimes = [time for time in showtimes if time > current_time]
        if filtered_showtimes:  # 현재 시간 이후의 상영 시간이 있을 경우만 추가
            filtered_time_table[title] = filtered_showtimes

    # 상영 스케줄이 없는 경우
    if not filtered_time_table:
        response_texts.append(f"'{theater_nm} {branch_nm}'점의 상영 스케줄이 없습니다.")
    else:
        response_texts.append(f"'{theater_nm} {branch_nm}'점의 상영 스케줄 입니다.")
        for title, showtimes in filtered_time_table.items():
            showtimes_str = " | ".join(showtimes)
            response_texts.append(f"{title}\n{showtimes_str}")

    response_texts.append("※ 실제 상영 스케줄과 차이가 있을 수 있습니다. 자세한 상영 스케줄은 영화관 홈페이지를 참고하시길 바랍니다.")

    # 다중 응답 형태로 응답 생성
    fulfillment_messages = [{"text": {"text": [text]}} for text in response_texts]
    return {"fulfillmentMessages": fulfillment_messages}


# 롯데시네마 모든 극장에 대해 상영 스케줄을 크롤링하는 메서드
def crawl_all_theater():
    url = 'https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx'
    date = datetime.today().strftime("%Y-%m-%d")
    all_theater_schedule = {}

    # 영화관 코드 파일 경로 설정
    current_dir = os.path.dirname(__file__)
    cinema_code_dir = os.path.join(current_dir, '..', 'cinemaCode')
    json_file_path = os.path.join(cinema_code_dir, 'lottecinema_cinemaCode.json')

    with open(json_file_path, 'r', encoding='utf-8') as f:
        theater_codes = json.load(f)

    for branch, cinema_id in theater_codes.items():
        dic = {
            "MethodName": "GetPlaySequence",
            "channelType": "HO",
            "osType": "",
            "osVersion": "",
            "playDate": date,
            "cinemaID": cinema_id,
            "representationMovieCode": ""
        }
        parameters = {"paramList": str(dic)}
        header = {'User-Agent': 'Mozilla/5.0'}

        try:
            response = requests.post(url, data=parameters, headers=header).json()
            movies_response = response['PlaySeqs']['Items']
            time_table = split_movies_by_no(movies_response)
            all_theater_schedule[branch] = time_table
        except Exception as e:
            print(f"Error retrieving data for {branch}: {e}")

    output_data = {
        "date": date,
        "timetable": all_theater_schedule
    }

    # timetable 폴더에 JSON 파일 저장
    output_dir = os.path.join(current_dir, '..', 'timetable')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'lottecinema_timetable.json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"상영 정보가 '{output_path}'에 저장되었습니다.")


# 저장된 상영스케줄 파일에서 정보 가져오기
def get_timetable(intent: str, request: dict):
    if intent == 'Req Showtime - LotteCinema':
        theater = request.get('queryResult').get('parameters').get('theater')
        branch = request.get('queryResult').get('parameters').get('Branch-LotteCinema')
    elif intent == 'Req Showtime - LotteCinema - AnotherBranch':
        theater = "롯데시네마"
        branch = request.get('queryResult').get('parameters').get('branch-lottecinema')

    if '점' == branch[-1]:
        branch = branch.replace('점', '')

    # 상영 스케줄 파일에서 정보 로드
    current_dir = os.path.dirname(__file__)
    time_table_dir = os.path.join(current_dir, '..', 'timetable')
    json_file_path = os.path.join(time_table_dir, 'lottecinema_timetable.json')

    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    timetable = data['timetable'].get(branch, {})
    return generate_response(theater, branch, timetable)


def split_movies_by_no(response):
    movie_no_list = get_movie_no_list(response)
    movie_dict = {}

    for movie_no in movie_no_list:
        movies = [item for item in response if item["MovieCode"] == movie_no]
        title = movies[0]["MovieNameKR"]
        timetable = get_time_table(movies)
        timetable.sort(key=lambda x: x[0])
        movie_dict[title] = timetable

    return movie_dict


def get_movie_no_list(response):
    movie_no_list = []
    for item in response:
        movie_no = item["MovieCode"]
        if movie_no not in movie_no_list:
            movie_no_list.append(movie_no)
    return movie_no_list


def get_time_table(movies):
    times = []
    for movie in movies:
        time = movie["StartTime"]
        times.append(time)
    return times


# 시작 전 롯데시네마의 타임테이블 검사
def check_timetable():
    current_dir = os.path.dirname(__file__)
    time_table_dir = os.path.join(current_dir, '..', 'timetable')
    json_file_path = os.path.join(time_table_dir, 'lottecinema_timetable.json')

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data["date"] != datetime.today().strftime("%Y-%m-%d"):
            os.remove(json_file_path)
            crawl_all_theater()
    except FileNotFoundError:
        crawl_all_theater()
