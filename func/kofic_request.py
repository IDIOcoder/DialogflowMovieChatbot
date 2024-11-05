from dotenv import load_dotenv
import os
import requests

load_dotenv()

KEY = os.environ.get('KOFIC_KEY')


# 영화 코드 가져오기 함수
def get_movie_code(movieNm):
    api_key = KEY
    url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json?key={api_key}&movieNm={movieNm}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        movie_list = data.get("movieListResult", {}).get("movieList", [])
        if movie_list:
            movie_code = movie_list[0].get("movieCd")
            return movie_code


# 영화 정보 가져오기 함수
def get_movie_info(req):
    movie_name = req.get('queryResult', {}).get('parameters', {}).get('any')
    movie_code = get_movie_code(movie_name)
    if movie_code:
        api_key = KEY
        url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json?key={api_key}&movieCd={movie_code}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            movie_info_data = data.get("movieInfoResult", {}).get("movieInfo", {})
            if movie_info_data:
                messages = [
                    {"text": {"text": [f"제목: {movie_info_data.get('movieNm', '정보 없음')}"]}},
                    {"text": {"text": [f"상영시간: {movie_info_data.get('showTm', '정보 없음')}분"]}},
                    {"text": {"text": [f"장르: {movie_info_data.get('genres', [{}])[0].get('genreNm', '정보 없음')}"]}},
                    {"text": {"text": [f"관람등급: {movie_info_data.get('audits', [{}])[0].get('watchGradeNm', '정보 없음')}"]}},
                    {"text": {"text": [f"감독: {', '.join([director.get('peopleNm', '정보 없음') for director in movie_info_data.get('directors', [])])}"]}},
                    {"text": {"text": [f"배우: {', '.join([actor.get('peopleNm', '정보 없음') for actor in movie_info_data.get('actors', [])[:5]])}"]}}
                ]
                return {'fulfillmentMessages': messages}


# 주간 박스오피스 순위 가져오기 함수
def get_weekly_boxoffice_rank():
    api_key = KEY
    target_date = '20241027'
    url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchWeeklyBoxOfficeList.json?key={api_key}&targetDt={target_date}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        box_office_list = data.get("boxOfficeResult", {}).get("weeklyBoxOfficeList", [])

        # 박스오피스 순위 정보를 각각의 메시지로 나눔
        messages = [{"text": {"text": [f"{item.get('rank', '정보 없음')}위: {item.get('movieNm', '정보 없음')} - 관객수: {item.get('audiCnt', '정보 없음')}명"]}} for item in box_office_list]
        return {'fulfillmentMessages': messages}


# 영화 추천 함수
def get_recommend_movie():
    api_key = KEY
    target_date = '20241027'
    url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchWeeklyBoxOfficeList.json?key={api_key}&targetDt={target_date}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        box_office_list = data.get("boxOfficeResult", {}).get("weeklyBoxOfficeList", [])

        # 상위 3개 영화를 추천하며 각각의 정보를 메시지로 나눔
        messages = [{"text": {"text": ["박스오피스 순위를 토대로 영화 몇 개를 추천드릴게요."]}}]
        messages += [{"text": {"text": [f"{item.get('rank', '정보 없음')}위: {item.get('movieNm', '정보 없음')} - 관객수: {item.get('audiCnt', '정보 없음')}명"]}} for item in box_office_list[:5]]
        print(f"[DEBUG] - RESULT : {messages}")
        return {'fulfillmentMessages': messages}



