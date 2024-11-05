import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime


# json으로부터 영화관 코드를 가져오는 메서드
def get_code(branch: str):
    current_dir = os.path.dirname(__file__)
    cinema_code_dir = os.path.join(current_dir, '..', 'cinemaCode')
    json_file_path = os.path.join(cinema_code_dir, 'cgv_cinemaCode.json')

    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data.get(branch)


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
        response_texts.append(f"'{theater_nm}{branch_nm}'의 상영 스케줄이 없습니다.")
    else:
        response_texts.append(f"'{theater_nm}{branch_nm}'의 상영 스케줄 입니다.")
        for title, showtimes in filtered_time_table.items():
            showtimes_str = " | ".join(showtimes)
            response_texts.append(f"{title}\n{showtimes_str}")

    response_texts.append("※ 실제 상영 스케줄과 차이가 있을 수 있습니다. 자세한 상영 스케줄은 영화관 홈페이지를 참고하시길 바랍니다.")

    # 다중 응답 형태로 응답 생성
    fulfillment_messages = [{"text": {"text": [text]}} for text in response_texts]
    return {"fulfillmentMessages": fulfillment_messages}


# 상영 시간을 중복 없이 정렬된 상태로 반환하는 메서드
def clean_and_sort_showtimes(showtimes):
    # 중복 제거하고 정렬하여 리스트 반환
    unique_showtimes = sorted(set(showtimes))
    return unique_showtimes


# 크롤링한 데이터를 정리하여 딕셔너리로 변환하는 메서드
def organize_movie_schedule(movies_data):
    movie_dict = {}
    for movie in movies_data:
        title = movie["title"]
        showtimes = movie["showtimes"]

        # 중복 제거 및 오름차순 정렬한 상영 시간 목록
        cleaned_showtimes = clean_and_sort_showtimes(showtimes)
        movie_dict[title] = cleaned_showtimes

    return movie_dict


# 씨네드셰프를 제외한 서울권 CGV극장 상영 스케줄 크롤링
def crawl_all_theater():
    # Chrome 옵션 설정
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])

    # 브라우저 열기
    driver = webdriver.Chrome(options=chrome_options)
    driver.delete_all_cookies()

    # 모든 극장 정보를 담을 딕셔너리
    all_theater_schedule = {}

    # JSON 파일에서 극장 코드를 로드
    current_dir = os.path.dirname(__file__)
    cinema_code_dir = os.path.join(current_dir, '..', 'cinemaCode')
    json_file_path = os.path.join(cinema_code_dir, 'cgv_cinemaCode.json')

    with open(json_file_path, 'r', encoding='utf-8') as f:
        theater_codes = json.load(f)

    # 오늘 날짜
    date = datetime.today().strftime("%Y-%m-%d")

    # 모든 극장에 대해 크롤링
    for branch, cinema_id in theater_codes.items():
        url = f"http://www.cgv.co.kr/theaters/?areacode=01&theaterCode={cinema_id}&date={date.replace('-', '')}"
        driver.get(url=url)

        movies_data = []  # 현재 극장의 영화 정보를 저장할 리스트

        try:
            # 상영 시간표가 포함된 iframe으로 이동
            innerIframe = driver.find_element(By.ID, "ifrm_movie_time_table")
            driver.switch_to.frame(innerIframe)

            movies = driver.find_elements(By.CLASS_NAME, "info-movie")
            for movie in movies:
                title = movie.find_element(By.TAG_NAME, "a").text

                # 상영 시간 정보 가져오기
                type_halls = movie.find_elements(By.XPATH, "../..//div[@class='type-hall']")
                showtimes_list = []

                for hall in type_halls:
                    timetable = hall.find_element(By.CLASS_NAME, "info-timetable")
                    showtimes = timetable.find_elements(By.TAG_NAME, "li")

                    for showtime in showtimes:
                        time_text = showtime.text.strip()
                        if "마감" not in time_text:
                            time_only = time_text.split("\n")[0]
                            showtimes_list.append(time_only)

                # 영화 데이터를 리스트에 추가
                movies_data.append({
                    "title": title,
                    "showtimes": showtimes_list
                })

        except Exception as e:
            print(f"Error retrieving data for {branch}: {e}")

        finally:
            # iframe에서 메인 페이지로 돌아가기
            driver.switch_to.default_content()

        # 현재 극장의 상영 정보를 딕셔너리 형태로 정리
        movie_schedule = organize_movie_schedule(movies_data)
        all_theater_schedule[branch] = movie_schedule  # 극장 이름을 키로, 상영 스케줄을 값으로 추가

    driver.quit()

    # JSON 데이터 구조 생성
    output_data = {
        "date": date,
        "timetable": all_theater_schedule
    }

    # 상위 폴더의 timetable 폴더에 JSON 파일 저장
    output_dir = os.path.join(current_dir, '..', 'timetable')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'cgv_timetable.json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"상영 정보가 '{output_path}'에 저장되었습니다.")


# 시작 전 CGV의 타임테이블 검사
def check_timetable():
    current_dir = os.path.dirname(__file__)
    time_table_dir = os.path.join(current_dir, '..', 'timetable')
    json_file_path = os.path.join(time_table_dir, 'cgv_timetable.json')

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if data["date"] != datetime.today().strftime("%Y-%m-%d"):  # 전날의 상영 스케줄인 경우
            os.remove(json_file_path)  # 이전날의 상영 스케줄 삭제
            crawl_all_theater()
    except FileNotFoundError:
        crawl_all_theater()


# 저장된 상영스케줄을 제공
def get_timetable(intent: str, request: dict):
    if intent == 'Req Showtime - CGV':
        theater = request.get('queryResult').get('parameters').get('theater')
        branch = request.get('queryResult').get('parameters').get('branch-cgv')
        print(f"[DEBUG] : Get Timetable of {theater}-{branch}")
    elif intent == 'Req Showtime - CGV - AnotherBranch':
        theater = "CGV"
        branch = request.get('queryResult').get('parameters').get('Branch-CGV')
        print(f"[DEBUG] : Get Timetable of {theater}-{branch}")

    if '점' == branch[-1]:
        branch = branch.replace('점', '')

    # 상영 스케줄 파일에서 정보 로드
    current_dir = os.path.dirname(__file__)
    time_table_dir = os.path.join(current_dir, '..', 'timetable')
    json_file_path = os.path.join(time_table_dir, 'cgv_timetable.json')

    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    timetable = data['timetable'][branch]
    return generate_response(theater, branch, timetable)

